import asyncio
from typing import Any, Dict, Callable, Awaitable, List


# ==============================
# 模拟 RunnableConfig
# ==============================
class RunnableConfig(dict):
    pass


# ==============================
# MCP 请求对象
# ==============================
class MCPToolCallRequest:
    def __init__(self, args: Dict[str, Any]):
        self.args = args

    def override(self, args: Dict[str, Any]):
        return MCPToolCallRequest(args)


# ==============================
# Fake Tool（模拟 MCP Tool）
# ==============================
class FakeTool:
    def __init__(self, name: str):
        self.name = name
        self._interceptors: List[Callable] = []

    async def _actual_invoke(self, request: MCPToolCallRequest):
        # 模拟真正执行
        print("👉 最终传入 Tool 的参数：")
        for k, v in request.args.items():
            print(f"   {k}: {v}")
        return {"status": "success", "received": request.args}

    async def ainvoke(self, args: Dict[str, Any]):
        request = MCPToolCallRequest(args)

        # 构造 interceptor chain
        async def call_chain(index, req):
            if index < len(self._interceptors):
                return await self._interceptors[index](
                    req,
                    lambda new_req: call_chain(index + 1, new_req)
                )
            else:
                return await self._actual_invoke(req)

        return await call_chain(0, request)


# ==============================
# Fake MCP Client
# ==============================
class FakeMCPClient:
    def __init__(self):
        self.tools = [
            FakeTool("my_tool")
        ]

    async def get_tools(self):
        return self.tools


# ==============================
# 核心函数（你的逻辑实现）
# ==============================
async def tool_with_runtime_injection(
        tool_name: str,
        config: RunnableConfig,
        **kwargs
) -> Any:
    client = config.get("configurable", {}).get("mcp_client")
    if not client:
        raise ValueError("MCP client not found in config")

    tools = await client.get_tools()
    tool = next((t for t in tools if t.name == tool_name), None)

    if not tool:
        raise ValueError(f"Tool {tool_name} not found")

    # runtime 上下文
    runtime_context = {
        "callbacks": config.get("callbacks"),
        "tags": config.get("tags"),
        "metadata": config.get("metadata"),
        "configurable": config.get("configurable", {})
    }

    # interceptor
    async def runtime_interceptor(request: MCPToolCallRequest, handler):
        modified_args = {
            **request.args,
            "__runtime": runtime_context,
            "__user_id": config.get("configurable", {}).get("user_id"),
            "__session_id": config.get("configurable", {}).get("session_id")
        }
        modified_request = request.override(args=modified_args)
        return await handler(modified_request)

    # 临时注入 interceptor
    original_interceptors = tool._interceptors.copy()
    tool._interceptors = [runtime_interceptor]

    try:
        return await tool.ainvoke(kwargs)
    finally:
        tool._interceptors = original_interceptors


# ==============================
# 测试入口
# ==============================
async def main():
    client = FakeMCPClient()

    config = RunnableConfig({
        "configurable": {
            "mcp_client": client,
            "user_id": "user_123",
            "session_id": "session_456",
            "tenant": "example_org"
        },
        "tags": ["production", "user_flow"],
        "metadata": {"request_id": "req_789"}
    })

    result = await tool_with_runtime_injection(
        "my_tool",
        config,
        param1="value1",
        param2="value2"
    )

    print("\n✅ 返回结果：")
    print(result)


if __name__ == "__main__":
    asyncio.run(main())