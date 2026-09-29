from deepagents import create_deep_agent
from langchain_classic.agents import AgentExecutor
from langchain_community.chat_models import ChatTongyi
from pprint import pprint

call_count = 0

def get_weather(city: str) -> str:
    """获取指定城市的天气。"""
    global call_count

    call_count += 1
    # print(f"[tool:get_weather] 第 {call_count} 次调用，city={city!r}")
    if call_count >= 2:
        result = f"在 {city} 总是阳光明媚！"
        # print(f"[tool:get_weather] 返回：{result}")
        return result
    result = "工具结果未就绪，请再次调用 get_weather 获取最终天气。"
    # print(f"[tool:get_weather] 返回：{result}")
    return result


llm = ChatTongyi(
            model="qwen-plus",
            api_key="",
            model_kwargs={
                "temperature": 0.0  # 让回答统一
            }
        )
agent = create_deep_agent(
    model=llm,
    tools=[get_weather],
    system_prompt=(
        "你是一个天气助手。回答天气问题时必须百分百依据 get_weather 工具返回。"
        "禁止使用常识、猜测、编造或补全天气信息。"
        "如果 get_weather 返回内容表示未就绪、需要再次调用或不是最终天气，"
        "你必须继续调用 get_weather，直到工具返回明确的最终天气结果。"
        "最终回答只能复述工具返回的天气结果。"
    ),
)

result = agent.invoke(
    {"messages": [{"role": "user", "content": "sf 的天气怎么样"}]}
)

print("\n[full result]")
pprint(result)

print("\n[agent messages]")
for index, message in enumerate(result["messages"], start=1):
    message_type = getattr(message, "type", type(message).__name__)
    message_content = getattr(message, "content", message)
    tool_calls = getattr(message, "tool_calls", None)
    print(f"{index}. [{message_type}] {message_content}")
    if tool_calls:
        print(f"   tool_calls={tool_calls}")

final_answer = result["messages"][-1].content
print("\n[final answer]")
print(final_answer)
