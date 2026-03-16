from deepagents import create_deep_agent
from langchain_classic.agents import AgentExecutor
from langchain_community.chat_models import ChatTongyi


def get_weather(city: str) -> str:
    """获取指定城市的天气。"""
    return f"在 {city} 总是阳光明媚！"
llm = ChatTongyi(
            model="qwen-plus",
            api_key="sk-12d7440948d94e27a9597ff57fe2a8c7",
            model_kwargs={
                "temperature": 0.0  # 让回答统一
            }
        )
agent = create_deep_agent(
    model=llm,
    tools=[get_weather],
    system_prompt="你是一个乐于助人的助手",
)
result = agent.invoke(
    {"messages": [{"role": "user", "content": "sf 的天气怎么样"}]}
)
final_answer = result["messages"][-1].content
print(final_answer)
