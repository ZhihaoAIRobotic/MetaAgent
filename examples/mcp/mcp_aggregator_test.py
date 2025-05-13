import sys
import os
import asyncio
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from metaagent.mcp.human_input_aggregator import HumanInputAggregator
from metaagent.config import Settings, LoggerSettings, MCPSettings, MCPServerSettings
from metaagent.context import initialize_context, get_current_context


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
                args=["-y", "@modelcontextprotocol/server-filesystem"],
            ),
        }
    )
)


async def main():
    await initialize_context(settings, store_globally=True)
    human_input_aggregator = HumanInputAggregator(
            name="finder",
            instruction="""You are an agent with access to the filesystem, 
            as well as the ability to fetch URLs. Your job is to identify 
            the closest match to a user's request, make the appropriate tool calls, 
            and return the URI and CONTENTS of the closest match.""",
            server_names=["fetch", "filesystem"],
        )
    async with human_input_aggregator:
        list_tools_result = await human_input_aggregator.list_tools()
        print(list_tools_result)


if __name__ == "__main__":
    asyncio.run(main())
