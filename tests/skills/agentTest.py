import uuid
from deepagents import create_deep_agent
from langchain_community.chat_models import ChatTongyi
from langchain_core.runnables import RunnableConfig

# =========================
# 你的原始 handler（不动）
# =========================
from src.friend.app.core.AgentTokenHandler import TongyiTokenHandler

i = 3
handler = TongyiTokenHandler()


# =========================
# 1️⃣ Tool（关键修改）
# =========================
def get_weather(city: str, config: RunnableConfig = None) -> str:
    """获取指定城市的天气。"""
    global i

    # ✅ 从 config 拿 sole_id
    sole_id = "NO_ID"
    if config:
        sole_id = config.get("configurable", {}).get("sole_id", "NO_ID")

    print(f"[TOOL] sole_id={sole_id}, city={city}")

    # if i >= 1:
    #     i -= 1
    #     return "你必须要再调用一次才可以获取数据"

    return f"在 {city} 总是阳光明媚！"


# =========================
# 2️⃣ LLM（不动）
# =========================
llm = ChatTongyi(
    model="qwen-plus",
    api_key="sk-12d7440948d94e27a9597ff57fe2a8c7",
    model_kwargs={"temperature": 0.0},
    callbacks=[handler],
)


# =========================
# 3️⃣ Deep Agent（不动）
# =========================
agent = create_deep_agent(
    model=llm,
    tools=[get_weather],
    system_prompt="你是一个乐于助人的助手",
)


# =========================
# 4️⃣ Middleware（核心）
# =========================
def middleware_invoke(agent, input_data: dict):
    # ✅ 自动生成唯一 ID
    sole_id = str(uuid.uuid4())
    print(f"[MIDDLEWARE] 生成 sole_id = {sole_id}")

    # ✅ 注入 config
    config = {
        "configurable": {
            "sole_id": sole_id
        }
    }

    # ✅ 关键：传入 config
    return agent.invoke(input_data, config=config)


# =========================
# 5️⃣ 运行
# =========================
if __name__ == "__main__":
    # result = middleware_invoke(
    #     agent,
    #     {"messages": [{"role": "user", "content": "sf 的天气怎么样"}]}
    # )
    sole_id = str(uuid.uuid4())
    data = {"messages": [{"role": "user", "content": "sf 的天气怎么样"}]}
    config = {
        "configurable": {
            "sole_id": sole_id
        }
    }
    result = agent.invoke(data, config=config)
    print(result)
    # final_answer = result["messages"][-1].content
    print("\n[FINAL ANSWER]")
    # print(final_answer)