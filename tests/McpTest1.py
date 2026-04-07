from langchain_core.runnables import RunnableConfig
from langchain_mcp_adapters.client import MultiServerMCPClient
from typing import Any, Dict

from langchain_mcp_adapters.interceptors import MCPToolCallRequest


async def tool_with_runtime_injection(
        tool_name: str,
        config: RunnableConfig,
        **kwargs
) -> Any:
    """
    Call an MCP tool with runtime context injection.

    Args:
        tool_name: Name of the MCP tool to call
        config: LangChain runnable config containing runtime context
        **kwargs: Tool arguments
    """
    client = config.get("configurable", {}).get("mcp_client")
    if not client:
        raise ValueError("MCP client not found in config")

    tools = await client.get_tools()
    tool = next((t for t in tools if t.name == tool_name), None)

    if not tool:
        raise ValueError(f"Tool {tool_name} not found")

    # Extract runtime from config
    runtime_context = {
        "callbacks": config.get("callbacks"),
        "tags": config.get("tags"),
        "metadata": config.get("metadata"),
        "configurable": config.get("configurable", {})
    }

    # Create interceptor that adds runtime
    async def runtime_interceptor(request: MCPToolCallRequest, handler):
        modified_args = {
            **request.args,
            "__runtime": runtime_context,
            "__user_id": config.get("configurable", {}).get("user_id"),
            "__session_id": config.get("configurable", {}).get("session_id")
        }
        modified_request = request.override(args=modified_args)
        return await handler(modified_request)

    # Apply interceptor temporarily
    original_interceptors = tool._interceptors.copy() if hasattr(tool, '_interceptors') else []
    tool._interceptors = [runtime_interceptor]

    try:
        return await tool.ainvoke(kwargs)
    finally:
        tool._interceptors = original_interceptors


# Usage
async def main():
    client = MultiServerMCPClient(connections={...})

    # Create config with runtime context
    config = RunnableConfig(
        configurable={
            "mcp_client": client,
            "user_id": "user_123",
            "session_id": "session_456",
            "tenant": "example_org"
        },
        tags=["production", "user_flow"],
        metadata={"request_id": "req_789"}
    )

    # Call tool with runtime injection
    result = await tool_with_runtime_injection(
        "my_tool",
        config,
        param1="value1",
        param2="value2"
    )
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())