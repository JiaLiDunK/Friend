# =========================
# pip install 依赖（先确保安装）
# =========================
# pip install langchain langchain-community langchain-mcp-adapters deepagents

import uuid
import asyncio
from typing import Any, Dict

from deepagents import create_deep_agent
from langchain_community.chat_models import ChatTongyi

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.interceptors import MCPToolCallRequest


# =========================
# 1️⃣ MCP Tool（从 metadata 取 sole_id）
# =========================
def get_weather(city: str, request: Dict[str, Any] = None) -> str:
    """获取指定城市的天气（从 metadata 拿 sole_id）"""

    sole_id = "NO_ID"

    # ✅ 从 metadata 获取
    if request and isinstance(request, dict):
        metadata = request.get("metadata", {})
        sole_id = metadata.get("sole_id", "NO_ID")

    print(f"[TOOL] sole_id={sole_id}, city={city}")

    return f"在 {city} 总是阳光明媚！"


# =========================
# 2️⃣ MCP Server（本地模拟）
# =========================
# ⚠️ 这里用最简单方式模拟一个 MCP tool server
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("weather_server")


@mcp.tool()
def weather(city: str, request: Dict[str, Any] = None) -> str:
    return get_weather(city, request)


# =========================
# 3️⃣ 拦截器（核心）
# =========================
async def inject_sole_id(request: MCPToolCallRequest, handler):
    """自动注入 sole_id 到 metadata"""

    sole_id = str(uuid.uuid4())

    # ✅ 初始化 metadata
    if request.metadata is None:
        request.metadata = {}

    request.metadata["sole_id"] = sole_id

    print(f"[INTERCEPTOR] 注入 sole_id = {sole_id}")

    return await handler(request)


# =========================
# 4️⃣ 主逻辑
# =========================
async def main():
    # 启动 MCP server（子进程方式）
    client = MultiServerMCPClient(
        {
            "weather": {
                "transport": "stdio",
                "command": "python",
                "args": ["__main__.py"],  # ⚠️ 关键：当前文件
            }
        },
        tool_interceptors=[inject_sole_id],  # ✅ 注册拦截器
    )

    # 获取 MCP tools
    tools = await client.get_tools()

    # LLM
    llm = ChatTongyi(
        model="qwen-plus",
        api_key="sk-",
        model_kwargs={"temperature": 0.0},
    )

    # Agent
    agent = create_deep_agent(
        model=llm,
        tools=tools,
        system_prompt="你是一个乐于助人的助手",
    )

    # 调用（不需要 config 了）
    result = await agent.ainvoke({
        "messages": [{"role": "user", "content": "sf 的天气怎么样"}]
    })

    print("\n[FINAL RESULT]")
    print(result)


# =========================
# 5️⃣ 入口（区分 server / client）
# =========================
if __name__ == "__main__":
    asyncio.run(main())