import sys
import os
import asyncio
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from metaagent.mcp.mcp_aggregator import MCPAggregator
from metaagent.config import Settings, LoggerSettings, MCPSettings, MCPServerSettings
from metaagent.mcp_app import MCPApp


settings = Settings(
    execution_engine="asyncio",
    logger=LoggerSettings(type="file", level="debug"),
    mcp=MCPSettings(
        servers={
            "fetch": MCPServerSettings(
                command="uvx",
                args=["mcp-server-fetch"],
            ),
            "filesystem": MCPServerSettings(
                command="npx",
                args=["-y", "@modelcontextprotocol/server-filesystem", "."],
            ),
        }
    )
)
setting_path = "/home/ubuntu/code_project/MetaAgent/examples/mcp/mcp_agent.config.yaml"

app = MCPApp(name="mcp_app", settings=setting_path)

async def main():
    """
    Method1: async with app.run() to manage the context
    """
    # async with app.run() as mcp_app:
    #     aggregator = await MCPAggregator.create(
    #             server_names=["fetch", "filesystem"],
    #             connection_persistence=True
    #         )
    #     async with aggregator:
    #         list_tools_result = await aggregator.list_tools()
    #         print(list_tools_result)
    #         result = await aggregator.call_tool("fetch", {"url": "https://scholar.google.com/"})
    #         print(result)
    
    """
    Method2: __aenter__ and __aexit__ to manage the context
    """
    # mcp_context_manager = app.run()
    # mcp_app = await mcp_context_manager.__aenter__()
    # aggregator = await MCPAggregator.create(
    #             server_names=["fetch", "filesystem"],
    #             connection_persistence=True
    #         )
    # list_tools_result = await aggregator.list_tools()
    # print(list_tools_result)
    # result = await aggregator.call_tool("fetch", {"url": "https://scholar.google.com/"})
    # print(result)
    # await aggregator.close()
    # await mcp_context_manager.__aexit__(None, None, None)

    """
    Method3: async with app.initialize() to manage the context
    """
    await app.initialize()
    aggregator = await MCPAggregator.create(
                server_names=["fetch", "filesystem"],
                connection_persistence=True
            )
    list_tools_result = await aggregator.list_tools()
    print(list_tools_result)
    result = await aggregator.call_tool("fetch", {"url": "https://scholar.google.com/"})
    print(result)
    await aggregator.close()
    await app.cleanup()
    

if __name__ == "__main__":
    asyncio.run(main())
