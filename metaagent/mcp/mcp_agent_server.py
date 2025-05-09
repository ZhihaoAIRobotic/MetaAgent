import asyncio
from mcp.server import NotificationOptions
from mcp.server.fastmcp import FastMCP
from mcp.server.stdio import stdio_server
from metaagent.executor.temporal import get_temporal_client

app = FastMCP("mcp-agent-server")



async def run():
    async with stdio_server() as (read_stream, write_stream):
        await app._mcp_server.run(
            read_stream,
            write_stream,
            app._mcp_server.create_initialization_options(
                notification_options=NotificationOptions(
                    tools_changed=True, resources_changed=True
                )
            ),
        )


@app.tool
async def run_workflow(query: str):
    """Run the workflow given its name or id"""
    pass


@app.tool
async def pause_workflow(workflow_id: str):
    """Pause a running workflow."""
    temporal_client = await get_temporal_client()
    handle = temporal_client.get_workflow_handle(workflow_id)
    await handle.signal("pause")


@app.tool
async def resume_workflow(workflow_id: str):
    """Resume a paused workflow."""
    temporal_client = await get_temporal_client()
    handle = temporal_client.get_workflow_handle(workflow_id)
    await handle.signal("resume")


async def provide_user_input(workflow_id: str, input_data: str):
    """Provide user/human input to a waiting workflow step."""
    temporal_client = await get_temporal_client()
    handle = temporal_client.get_workflow_handle(workflow_id)
    await handle.signal("human_input", input_data)


if __name__ == "__main__":
    asyncio.run(run())
