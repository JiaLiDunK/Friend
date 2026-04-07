import uuid
from deepagents import create_deep_agent
from langchain_core.runnables import RunnableConfig
from langchain_community.chat_models import ChatTongyi

# =========================
# 1️⃣ 模拟 MCP Server
# =========================
def mock_mcp_server(payload: dict):
    city = payload.get("city")
    sole_id = payload.get("sole_id")

    print(f"[MCP SERVER] 收到请求: city={city}, sole_id={sole_id}")

    return f"{city} 天气晴朗 ☀️"


# =========================
# 2️⃣ MCP Client（简单封装）
# =========================
def call_mcp_tool(args: dict):
    # 实际这里可以是 HTTP / RPC
    return mock_mcp_server(args)


# =========================
# 3️⃣ ⭐桥接 Tool（关键）
# =========================
def get_weather(city: str, config: RunnableConfig = None) -> str:
    """
    LangChain Tool（桥接层）：
    - 从 config 拿 sole_id
    - 注入到 MCP 请求
    """
    sole_id = None
    if config:
        sole_id = config.get("configurable", {}).get("sole_id")

    print(f"[BRIDGE TOOL] 注入 sole_id={sole_id}")

    # 👇 手动传给 MCP
    return call_mcp_tool({
        "city": city,
        "sole_id": sole_id
    })


# =========================
# 4️⃣ LLM（随便一个）
# =========================
llm = ChatTongyi(
    model="qwen-plus",
    api_key="sk-12d7440948d94e27a9597ff57fe2a8c7",  # 换成你的key
    model_kwargs={"temperature": 0}
)


# =========================
# 5️⃣ Deep Agent
# =========================
agent = create_deep_agent(
    model=llm,
    tools=[get_weather],
    system_prompt="你是一个天气助手，必须调用工具获取天气，不允许编造"
)


# =========================
# 6️⃣ Middleware（生成 sole_id）
# =========================
def middleware_invoke(agent, data):
    sole_id = str(uuid.uuid4())
    print(f"[MIDDLEWARE] 生成 sole_id = {sole_id}")

    config = {
        "configurable": {
            "sole_id": sole_id
        }
    }

    return agent.invoke(data, config=config)


# =========================
# 7️⃣ 运行
# =========================
if __name__ == "__main__":
    result = middleware_invoke(
        agent,
        {"messages": [{"role": "user", "content": "sf 的天气怎么样"}]}
    )

    print("\n[FINAL ANSWER]")
    print(result["messages"][-1].content)