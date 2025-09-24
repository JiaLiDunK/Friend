from langchain_community.chat_models.tongyi import ChatTongyi
from langchain.agents import create_openai_tools_agent, AgentExecutor
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools import tool

# 定义一个简单工具
@tool
def insert_record(table: str, values: dict) -> str:
    """往指定表插入一条数据"""
    return f"成功插入 {values} 到 {table}"

tools = [insert_record]

# 选择模型
llm = ChatTongyi(model="qwen-plus", api_key="sk-")

# 定义 prompt
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个智能助手，可以调用工具完成任务。"),
    ("user", "{input}"),
    MessagesPlaceholder("agent_scratchpad"),
])

# 创建 agent 和 executor
agent = create_openai_tools_agent(llm, tools, prompt)
executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# ---- 1. 只跑 agent ----
# print("\n===== 只跑 agent =====")
# agent_result = agent.invoke({"input": "请在 users 表插入一个用户，名字是 Alice，年龄是 25"})
# print("Agent 输出：", agent_result)

# ---- 2. 跑 executor ----
print("\n===== 跑 executor =====")
executor_result = executor.invoke({"input": "请在 users 表插入一个用户，名字是 Alice，年龄是 25"})
print("Executor 输出：", executor_result["output"])
