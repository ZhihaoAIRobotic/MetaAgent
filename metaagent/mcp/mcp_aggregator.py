import asyncio
from typing import List, Literal, Dict, Optional, TypeVar, TYPE_CHECKING

from pydantic import BaseModel, ConfigDict
from mcp.client.session import ClientSession
from mcp.server.lowlevel.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolResult,
    GetPromptResult,
    ListPromptsResult,
    ListToolsResult,
    Prompt,
    Tool,
    TextContent,
)

from metaagent.event_progress import ProgressAction
from metaagent.logging.logger import get_logger
from metaagent.mcp.gen_client import gen_client

from metaagent.context_dependent import ContextDependent
from metaagent.mcp.metaagent_client_session import MCPAgentClientSession
from metaagent.mcp.mcp_connection_manager import MCPConnectionManager

if TYPE_CHECKING:
    from metaagent.context import Context


logger = get_logger(
    __name__
)  # This will be replaced per-instance when agent_name is available

SEP = "_"

# Define type variables for the generalized method
T = TypeVar("T")
R = TypeVar("R")


class NamespacedTool(BaseModel):
    """
    A tool that is namespaced by server name.
    """

    tool: Tool
    server_name: str
    namespaced_tool_name: str


class NamespacedPrompt(BaseModel):
    """
    A prompt that is namespaced by server name.
    """

    prompt: Prompt
    server_name: str
    namespaced_prompt_name: str


class MCPAggregator(ContextDependent):
    """
    Aggregates multiple MCP servers. When a developer calls, e.g. call_tool(...),
    the aggregator searches all servers in its list for a server that provides that tool.
    """

    initialized: bool = False
    """Whether the aggregator has been initialized with tools and resources from all servers."""

    connection_persistence: bool = False
    """Whether to maintain a persistent connection to the server."""

    server_names: List[str]
    """A list of server names to connect to."""

    model_config = ConfigDict(extra="allow", arbitrary_types_allowed=True)

    async def __aenter__(self):
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    def __init__(
        self,
        server_names: List[str],
        connection_persistence: bool = True,  # Default to True for better stability
        context: Optional["Context"] = None,
        name: str = None,
        **kwargs,
    ):
        """
        :param server_names: A list of server names to connect to.
        :param connection_persistence: Whether to maintain persistent connections to servers (default: True).
        Note: The server names must be resolvable by the gen_client function, and specified in the server registry.
        """
        super().__init__(
            context=context,
            **kwargs,
        )

        self.server_names = server_names
        self.connection_persistence = connection_persistence
        self.agent_name = name
        self._persistent_connection_manager: MCPConnectionManager = None

        # Set up logger with agent name in namespace if available
        global logger
        logger_name = f"{__name__}.{name}" if name else __name__
        logger = get_logger(logger_name)

        # Maps namespaced_tool_name -> namespaced tool info
        self._namespaced_tool_map: Dict[str, NamespacedTool] = {}
        # Maps server_name -> list of tools
        self._server_to_tool_map: Dict[str, List[NamespacedTool]] = {}
        self._tool_map_lock = asyncio.Lock()

        # Maps namespaced_prompt_name -> namespaced prompt info
        self._namespaced_prompt_map: Dict[str, NamespacedPrompt] = {}
        # Cache for prompt objects, maps server_name -> list of prompt objects
        self._server_to_prompt_map: Dict[str, List[NamespacedPrompt]] = {}
        self._prompt_map_lock = asyncio.Lock()

    async def initialize(self, force: bool = False):
        """Initialize the application."""
        if self.initialized and not force:
            return

        # Keep a connection manager to manage persistent connections for this aggregator
        if self.connection_persistence:
            # Try to get existing connection manager from context
            # TODO: saqadri (FA1) - verify
            # Initialize connection manager tracking on the context if not present
            # These are placed on the context since it's shared across aggregators

            connection_manager: MCPConnectionManager | None = None

            if not hasattr(self.context, "_mcp_connection_manager_lock"):
                self.context._mcp_connection_manager_lock = asyncio.Lock()

            if not hasattr(self.context, "_mcp_connection_manager_ref_count"):
                self.context._mcp_connection_manager_ref_count = int(0)

            async with self.context._mcp_connection_manager_lock:
                self.context._mcp_connection_manager_ref_count += 1

                if hasattr(self.context, "_mcp_connection_manager"):
                    connection_manager = self.context._mcp_connection_manager
                else:
                    connection_manager = MCPConnectionManager(
                        self.context.server_registry
                    )
                    await connection_manager.__aenter__()
                    self.context._mcp_connection_manager = connection_manager

                self._persistent_connection_manager = connection_manager

        await self.load_servers()
        self.initialized = True

    async def close(self):
        """
        Close all persistent connections when the aggregator is deleted.
        """
        # TODO: saqadri (FA1) - Verify implementation
        if not self.connection_persistence or not self._persistent_connection_manager:
            return

        try:
            # We only need to manage reference counting if we're using connection persistence
            if hasattr(self.context, "_mcp_connection_manager_lock") and hasattr(
                self.context, "_mcp_connection_manager_ref_count"
            ):
                async with self.context._mcp_connection_manager_lock:
                    # Decrement the reference count
                    self.context._mcp_connection_manager_ref_count -= 1
                    current_count = self.context._mcp_connection_manager_ref_count
                    logger.debug(f"Decremented connection ref count to {current_count}")

                    # Only proceed with cleanup if we're the last user
                    if current_count == 0:
                        logger.info(
                            "Last aggregator closing, shutting down all persistent connections..."
                        )

                        if (
                            hasattr(self.context, "_mcp_connection_manager")
                            and self.context._mcp_connection_manager
                            == self._persistent_connection_manager
                        ):
                            # Add timeout protection for the disconnect operation
                            try:
                                await asyncio.wait_for(
                                    self._persistent_connection_manager.disconnect_all(),
                                    timeout=5.0,
                                )
                            except asyncio.TimeoutError:
                                logger.warning(
                                    "Timeout during disconnect_all(), forcing shutdown"
                                )

                            # Ensure the exit method is called regardless
                            try:
                                await self._persistent_connection_manager.__aexit__(
                                    None, None, None
                                )
                            except Exception as e:
                                logger.error(
                                    f"Error during connection manager __aexit__: {e}"
                                )

                            # Clean up the connection manager from the context
                            delattr(self.context, "_mcp_connection_manager")
                            logger.info(
                                "Connection manager successfully closed and removed from context"
                            )

            self.initialized = False
        except Exception as e:
            logger.error(f"Error during connection manager cleanup: {e}", exc_info=True)
            # TODO: saqadri (FA1) - Even if there's an error, we should mark ourselves as uninitialized
            self.initialized = False

    @classmethod
    async def create(
        cls,
        server_names: List[str],
        connection_persistence: bool = False,
    ) -> "MCPAggregator":
        """
        Factory method to create and initialize an MCPAggregator.
        Use this instead of constructor since we need async initialization.
        If connection_persistence is True, the aggregator will maintain a
        persistent connection to the servers for as long as this aggregator is around.
        By default we do not maintain a persistent connection.
        """

        logger.info(f"Creating MCPAggregator with servers: {server_names}")

        instance = cls(
            server_names=server_names,
            connection_persistence=connection_persistence,
        )

        try:
            await instance.__aenter__()

            logger.debug("Loading servers...")
            await instance.load_servers()

            logger.debug("MCPAggregator created and initialized.")
            return instance
        except Exception as e:
            logger.error(f"Error creating MCPAggregator: {e}")
            await instance.__aexit__(None, None, None)

    async def load_server(self, server_name: str):
        """
        Load tools and prompts from a single server and update the index of namespaced tool/prompt names for that server.
        """

        if server_name not in self.server_names:
            raise ValueError(f"Server '{server_name}' not found in server list")

        _, tools, prompts = await self._fetch_capabilities(server_name)

        # Process tools
        async with self._tool_map_lock:
            self._server_to_tool_map[server_name] = []
            for tool in tools:
                namespaced_tool_name = f"{server_name}{SEP}{tool.name}"
                namespaced_tool = NamespacedTool(
                    tool=tool,
                    server_name=server_name,
                    namespaced_tool_name=namespaced_tool_name,
                )

                self._namespaced_tool_map[namespaced_tool_name] = namespaced_tool
                self._server_to_tool_map[server_name].append(namespaced_tool)

        # Process prompts
        async with self._prompt_map_lock:
            self._server_to_prompt_map[server_name] = []
            for prompt in prompts:
                namespaced_prompt_name = f"{server_name}{SEP}{prompt.name}"
                namespaced_prompt = NamespacedPrompt(
                    prompt=prompt,
                    server_name=server_name,
                    namespaced_prompt_name=namespaced_prompt_name,
                )

                self._namespaced_prompt_map[namespaced_prompt_name] = namespaced_prompt
                self._server_to_prompt_map[server_name].append(namespaced_prompt)

        logger.debug(
            f"MCP Aggregator initialized for server '{server_name}'",
            data={
                "progress_action": ProgressAction.INITIALIZED,
                "server_name": server_name,
                "agent_name": self.agent_name,
                "tool_count": len(tools),
                "prompt_count": len(prompts),
            },
        )

        return tools, prompts

    async def load_servers(self, force: bool = False):
        """
        Discover tools and prompts from each server in parallel and build an index of namespaced tool/prompt names.
        """

        if self.initialized and not force:
            logger.debug("MCPAggregator already initialized. Skipping reload.")
            return

        async with self._tool_map_lock:
            self._namespaced_tool_map.clear()
            self._server_to_tool_map.clear()

        async with self._prompt_map_lock:
            self._namespaced_prompt_map.clear()
            self._server_to_prompt_map.clear()

        # TODO: saqadri (FA1) - Verify that this can be removed
        # if self.connection_persistence:
        #     # Start all the servers
        #     await asyncio.gather(
        #         *(self._start_server(server_name) for server_name in self.server_names),
        #         return_exceptions=True,
        #     )

        # Load tools and prompts from all servers concurrently
        results = await asyncio.gather(
            *(self.load_server(server_name) for server_name in self.server_names),
            return_exceptions=True,
        )

        for result in results:
            if isinstance(result, BaseException):
                logger.error(
                    f"Error loading server data: {result}. Attempting to continue"
                )
                continue

        self.initialized = True

    async def get_capabilities(self, server_name: str):
        """Get server capabilities if available."""
        if self.connection_persistence:
            try:
                server_conn = await self._persistent_connection_manager.get_server(
                    server_name, client_session_factory=MCPAgentClientSession
                )
                # TODO: saqadri (FA1) - verify
                # server_capabilities is a property, not a coroutine
                return server_conn.server_capabilities
            except Exception as e:
                logger.warning(
                    f"Error getting capabilities for server '{server_name}': {e}"
                )
                return None
        else:
            logger.debug(
                f"Creating temporary connection to server: {server_name}",
                data={
                    "progress_action": ProgressAction.STARTING,
                    "server_name": server_name,
                    "agent_name": self.agent_name,
                },
            )
            async with self.context.server_registry.start_server(
                server_name, client_session_factory=MCPAgentClientSession
            ) as session:
                try:
                    initialize_result = await session.initialize()
                    return initialize_result.capabilities
                except Exception as e:
                    logger.warning(
                        f"Error getting capabilities for server '{server_name}': {e}"
                    )
                    return None

    async def refresh(self, server_name: str | None = None):
        """
        Refresh the tools and prompts from the specified server or all servers.
        """
        if server_name:
            await self.load_server(server_name)
        else:
            await self.load_servers(force=True)

    async def list_servers(self) -> List[str]:
        """Return the list of server names aggregated by this agent."""
        if not self.initialized:
            await self.load_servers()

        return self.server_names

    async def list_tools(self, server_name: str | None = None) -> ListToolsResult:
        """
        :return: Tools from all servers aggregated, and renamed to be dot-namespaced by server name.
        """
        if not self.initialized:
            await self.load_servers()

        if server_name:
            return ListToolsResult(
                prompts=[
                    namespaced_tool.tool.model_copy(
                        update={"name": namespaced_tool.namespaced_tool_name}
                    )
                    for namespaced_tool in self._server_to_tool_map.get(server_name, [])
                ]
            )

        return ListToolsResult(
            tools=[
                namespaced_tool.tool.model_copy(update={"name": namespaced_tool_name})
                for namespaced_tool_name, namespaced_tool in self._namespaced_tool_map.items()
            ]
        )

    async def call_tool(
        self, name: str, arguments: dict | None = None
    ) -> CallToolResult:
        """
        Call a namespaced tool, e.g., 'server_name.tool_name'.
        """
        if not self.initialized:
            await self.load_servers()

        server_name: str = None
        local_tool_name: str = None

        # Use the helper method to parse the capability name
        server_name, local_tool_name = self._parse_capability_name(name, "tool")

        if server_name is None or local_tool_name is None:
            logger.error(f"Error: Tool '{name}' not found")
            return CallToolResult(
                isError=True,
                content=[TextContent(type="text", text=f"Tool '{name}' not found")],
            )

        logger.info(
            "Requesting tool call",
            data={
                "progress_action": ProgressAction.CALLING_TOOL,
                "tool_name": local_tool_name,
                "server_name": server_name,
                "agent_name": self.agent_name,
            },
        )

        async def try_call_tool(client: ClientSession):
            try:
                return await client.call_tool(name=local_tool_name, arguments=arguments)
            except Exception as e:
                return CallToolResult(
                    isError=True,
                    content=[
                        TextContent(
                            type="text",
                            text=f"Failed to call tool '{local_tool_name}' on server '{server_name}': {str(e)}",
                        )
                    ],
                )

        if self.connection_persistence:
            server_connection = await self._persistent_connection_manager.get_server(
                server_name, client_session_factory=MCPAgentClientSession
            )
            return await try_call_tool(server_connection.session)
        else:
            logger.debug(
                f"Creating temporary connection to server: {server_name}",
                data={
                    "progress_action": ProgressAction.STARTING,
                    "server_name": server_name,
                    "agent_name": self.agent_name,
                },
            )
            async with gen_client(
                server_name, server_registry=self.context.server_registry
            ) as client:
                result = await try_call_tool(client)
                logger.debug(
                    f"Closing temporary connection to server: {server_name}",
                    data={
                        "progress_action": ProgressAction.SHUTDOWN,
                        "server_name": server_name,
                        "agent_name": self.agent_name,
                    },
                )
                return result

    async def list_prompts(self, server_name: str | None = None) -> ListPromptsResult:
        """
        :return: Prompts from all servers aggregated, and renamed to be dot-namespaced by server name.
        """
        if not self.initialized:
            await self.load_servers()

        if server_name:
            return ListPromptsResult(
                prompts=[
                    namespaced_prompt.prompt.model_copy(
                        update={"name": namespaced_prompt.namespaced_prompt_name}
                    )
                    for namespaced_prompt in self._server_to_prompt_map.get(
                        server_name, []
                    )
                ]
            )

        return ListPromptsResult(
            prompts=[
                namespaced_prompt.prompt.model_copy(
                    update={"name": namespaced_prompt_name}
                )
                for namespaced_prompt_name, namespaced_prompt in self._namespaced_prompt_map.items()
            ]
        )

    async def get_prompt(
        self, name: str, arguments: dict[str, str] | None = None
    ) -> GetPromptResult:
        """
        Get a prompt from a server.

        Args:
            name: Name of the prompt, optionally namespaced with server name
                using the format 'server_name-prompt_name'
            arguments: Optional dictionary of string arguments to pass to the prompt template
                for prompt template resolution

        Returns:
            Fully resolved prompt returned by the server
        """
        if not self.initialized:
            await self.load_servers()

        server_name, local_prompt_name = self._parse_capability_name(name, "prompt")
        if server_name is None or local_prompt_name is None:
            logger.error(f"Error: Prompt '{name}' not found")
            return GetPromptResult(
                isError=True, description=f"Prompt '{name}' not found", messages=[]
            )

        logger.info(
            "Requesting prompt",
            data={
                # TODO: saqadri (FA1) - update progress action
                "progress_action": ProgressAction.CALLING_TOOL,
                "tool_name": local_prompt_name,
                "server_name": server_name,
                "agent_name": self.agent_name,
            },
        )

        async def try_get_prompt(client: ClientSession):
            try:
                return await client.get_prompt(
                    name=local_prompt_name, arguments=arguments
                )
            except Exception as e:
                return GetPromptResult(
                    isError=True,
                    description=f"Failed to call tool '{local_prompt_name}' on server '{server_name}': {str(e)}",
                    messages=[],
                )

        result: GetPromptResult = GetPromptResult(messages=[])
        if self.connection_persistence:
            server_connection = await self._persistent_connection_manager.get_server(
                server_name, client_session_factory=MCPAgentClientSession
            )
            result = await try_get_prompt(server_connection.session)
        else:
            logger.debug(
                f"Creating temporary connection to server: {server_name}",
                data={
                    "progress_action": ProgressAction.STARTING,
                    "server_name": server_name,
                    "agent_name": self.agent_name,
                },
            )
            async with gen_client(
                server_name, server_registry=self.context.server_registry
            ) as client:
                result = await try_get_prompt(client)
                logger.debug(
                    f"Closing temporary connection to server: {server_name}",
                    data={
                        "progress_action": ProgressAction.SHUTDOWN,
                        "server_name": server_name,
                        "agent_name": self.agent_name,
                    },
                )

        # Add namespaced name and source server to the result
        # TODO: saqadri (FA1) - this code shouldn't be here.
        # It should be wherever the prompt is being displayed
        if result and result.messages:
            result.server_name = server_name
            result.prompt_name = local_prompt_name
            result.namespaced_name = f"{server_name}{SEP}{local_prompt_name}"

            # Store the arguments in the result for display purposes
            if arguments:
                result.arguments = arguments

    def _parse_capability_name(
        self, name: str, capability: Literal["tool", "prompt"]
    ) -> tuple[str, str]:
        """
        Parse a capability name into server name and local capability name.

        Args:
            name: The tool or prompt name, possibly namespaced
            capability: The type of capability, either 'tool' or 'prompt'

        Returns:
            Tuple of (server_name, local_name)
        """
        # First check if this is a namespaced name with a valid server prefix
        if SEP in name:
            parts = name.split(SEP)

            # Try matching from longest possible prefix to shortest
            for i in range(len(parts) - 1, 0, -1):
                prefix = SEP.join(parts[:i])
                if prefix in self.server_names:
                    return prefix, SEP.join(parts[i:])

        # If no server name prefix is found, search all servers for a capability with this exact name
        if capability == "tool":
            capability_map = self._server_to_tool_map

            def getter(item: NamespacedTool):
                return item.tool.name
        elif capability == "prompt":
            capability_map = self._server_to_prompt_map

            def getter(item: NamespacedPrompt):
                return item.prompt.name
        else:
            raise ValueError(f"Unsupported capability: {capability}")

        # Search across all servers
        for srv_name, items in capability_map.items():
            for item in items:
                if getter(item) == name:
                    return srv_name, name

        # No match found
        return None, None

    async def _start_server(self, server_name: str):
        if self.connection_persistence:
            logger.info(
                f"Creating persistent connection to server: {server_name}",
                data={
                    "progress_action": ProgressAction.STARTING,
                    "server_name": server_name,
                    "agent_name": self.agent_name,
                },
            )

            server_conn = await self._persistent_connection_manager.get_server(
                server_name, client_session_factory=MCPAgentClientSession
            )

            logger.info(
                f"MCP Server initialized for agent '{self.agent_name}'",
                data={
                    "progress_action": ProgressAction.STARTING,
                    "server_name": server_name,
                    "agent_name": self.agent_name,
                },
            )

            return server_conn.session
        else:
            async with gen_client(
                server_name, server_registry=self.context.server_registry
            ) as client:
                return client

    async def _fetch_tools(self, client: ClientSession, server_name: str) -> List[Tool]:
        # Only fetch tools if the server supports them
        capabilities = await self.get_capabilities(server_name)
        if not capabilities or not capabilities.tools:
            logger.debug(f"Server '{server_name}' does not support tools")
            return []

        tools: List[Tool] = []
        try:
            result = await client.list_tools()
            if not result:
                return []

            cursor = result.nextCursor
            tools.extend(result.tools or [])

            while cursor:
                result = await client.list_tools(cursor=cursor)
                if not result:
                    return tools

                cursor = result.nextCursor
                tools.extend(result.tools or [])

            return tools
        except Exception as e:
            logger.error(f"Error loading tools from server '{server_name}'", data=e)
            return tools

    async def _fetch_prompts(
        self, client: ClientSession, server_name: str
    ) -> List[Prompt]:
        # Only fetch prompts if the server supports them
        capabilities = await self.get_capabilities(server_name)
        if not capabilities or not capabilities.prompts:
            logger.debug(f"Server '{server_name}' does not support prompts")
            return []

        prompts: List[Prompt] = []

        try:
            result = await client.list_prompts()
            if not result:
                return prompts

            cursor = result.nextCursor
            prompts.extend(result.prompts or [])

            while cursor:
                result = await client.list_prompts(cursor=cursor)
                if not result:
                    return prompts

                cursor = result.nextCursor
                prompts.extend(result.prompts or [])

            return prompts
        except Exception as e:
            logger.error(f"Error loading prompts from server '{server_name}': {e}")
            return prompts

    async def _fetch_capabilities(self, server_name: str):
        tools: List[Tool] = []
        prompts: List[Prompt] = []

        if self.connection_persistence:
            server_connection = await self._persistent_connection_manager.get_server(
                server_name, client_session_factory=MCPAgentClientSession
            )
            tools = await self._fetch_tools(server_connection.session, server_name)
            prompts = await self._fetch_prompts(server_connection.session, server_name)
        else:
            async with gen_client(
                server_name, server_registry=self.context.server_registry
            ) as client:
                tools = await self._fetch_tools(client, server_name)
                prompts = await self._fetch_prompts(client, server_name)

        return server_name, tools, prompts


class MCPCompoundServer(Server):
    """
    A compound server (server-of-servers) that aggregates multiple MCP servers and is itself an MCP server
    """

    def __init__(self, server_names: List[str], name: str = "MCPCompoundServer"):
        super().__init__(name)
        self.aggregator = MCPAggregator(server_names)

        # Register handlers for tools, prompts
        # TODO: saqadri - once we support resources, add handlers for those as well
        self.list_tools()(self._list_tools)
        self.call_tool()(self._call_tool)
        self.list_prompts()(self._list_prompts)
        self.get_prompt()(self._get_prompt)

    async def _list_tools(self) -> List[Tool]:
        """List all tools aggregated from connected MCP servers."""
        tools_result = await self.aggregator.list_tools()
        return tools_result.tools

    async def _call_tool(
        self, name: str, arguments: dict | None = None
    ) -> CallToolResult:
        """Call a specific tool from the aggregated servers."""
        try:
            result = await self.aggregator.call_tool(name=name, arguments=arguments)
            return result.content
        except Exception as e:
            return CallToolResult(
                isError=True,
                content=[
                    TextContent(type="text", text=f"Error calling tool: {str(e)}")
                ],
            )

    async def _list_prompts(self) -> List[Prompt]:
        """List available prompts from the connected MCP servers."""
        list_prompts_result = await self.aggregator.list_prompts()
        return list_prompts_result.prompts

    async def _get_prompt(
        self, name: str, arguments: dict[str, str] | None = None
    ) -> GetPromptResult:
        """
        Get a prompt from the aggregated servers.

        Args:
            name: Name of the prompt to get (optionally namespaced)
            arguments: Optional dictionary of string arguments for prompt templating
        """
        try:
            result = await self.aggregator.get_prompt(name=name, arguments=arguments)
            return result
        except Exception as e:
            return GetPromptResult(
                description=f"Error getting prompt: {e}", messages=[]
            )

    async def run_stdio_async(self) -> None:
        """Run the server using stdio transport."""
        async with stdio_server() as (read_stream, write_stream):
            await self.run(
                read_stream=read_stream,
                write_stream=write_stream,
                initialization_options=self.create_initialization_options(),
            )
