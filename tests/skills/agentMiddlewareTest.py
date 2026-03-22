import uuid
from typing import Any

from langchain_core.tools import tool
from langchain_core.runnables import RunnableLambda
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI


# =========================
# 1️⃣ 定义 Tool（模拟 MCP 工具）
# =========================
@tool
def my_tool(query: str, config: RunnableConfig) -> str:
    sole_id = config.get("configurable", {}).get("sole_id", "NO_ID")
    print(f"[TOOL] 收到调用, sole_id = {sole_id}, query = {query}")
    return f"Tool result for: {query}"


# =========================
# 2️⃣ 构建 Agent（deep agent 简化版）
# =========================
llm = ChatOpenAI(
    model="gpt-4o-mini",  # 你可以换成本地模型
    temperature=0
)

tools = [my_tool]

llm_with_tools = llm.bind_tools(tools)


def agent_logic(input_dict: dict, config: RunnableConfig) -> Any:
    """
    模拟 deep agent 行为：
    - LLM 决定是否调用工具
    - 自动把 config 透传给 tool
    """
    messages = [HumanMessage(content=input_dict["input"])]

    response = llm_with_tools.invoke(messages, config=config)

    # 如果 LLM 决定调用工具
    if response.tool_calls:
        for tool_call in response.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]

            if tool_name == "my_tool":
                return my_tool.invoke(tool_args, config=config)

    return response.content


agent = RunnableLambda(agent_logic)


# =========================
# 3️⃣ Middleware（关键）
# =========================
def middleware_invoke(agent, input_data: dict):
    """
    模拟 middleware：
    - 自动生成 sole_id
    - 注入到 config
    """
    sole_id = str(uuid.uuid4())
    print(f"[MIDDLEWARE] 生成 sole_id = {sole_id}")

    config = {
        "configurable": {
            "sole_id": sole_id
        }
    }

    return agent.invoke(input_data, config=config)


# =========================
# 4️⃣ 运行测试
# =========================
if __name__ == "__main__":
    result = middleware_invoke(
        agent,
        {"input": "请帮我调用工具查询一下天气"}
    )

    print("\n[FINAL RESULT]")
    print(result)