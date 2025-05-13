import sys
import os
from pathlib import Path
import asyncio
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from metaagent.mcp.human_input_aggregator import HumanInputAggregator
from metaagent.mcp_app import MCPApp
from metaagent.config import Settings, LoggerSettings, MCPSettings, MCPServerSettings


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
    async with app.run() as agent_app:
        human_input_aggregator = HumanInputAggregator(
            name="finder",
            instruction="""You are an agent with access to the filesystem, 
            as well as the ability to fetch URLs. Your job is to identify 
            the closest match to a user's request, make the appropriate tool calls, 
            and return the URI and CONTENTS of the closest match.""",
            server_names=["fetch", "filesystem"],
            # connection_persistence=False
        )
        async with human_input_aggregator:
            list_tools_result = await human_input_aggregator.list_tools()
            # print(list_tools_result)

            result = await human_input_aggregator.call_tool(
            name="read_file",
            arguments={"path": str(Path.cwd() / "mcp-agent.jsonl")},
            )
            # print(result)


if __name__ == "__main__":
    asyncio.run(main())
