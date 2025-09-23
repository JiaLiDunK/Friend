from langchain_community.chat_models.tongyi import ChatTongyi
from langchain.agents import create_openai_tools_agent, AgentExecutor
from langchain.tools import tool

# 1. 定义 SQL 写入工具
@tool
def insert_record(table: str, values: dict) -> str:
    """往指定表插入一条数据"""
    print(f"插入数据到 {table}: {values}")
    return "数据写入成功"

tools = [insert_record]

# 2. 选择模型
llm = ChatTongyi(model="qwen-plus", api_key="sk-")

# 3. 自己写提示词，替代 hub.pull
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder

prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个智能助手，可以调用工具完成任务。"),
    ("user", "{input}"),
    MessagesPlaceholder("agent_scratchpad"),
])

# 4. 创建 agent
agent = create_openai_tools_agent(llm, tools, prompt)
executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# 5. 调用
result = executor.invoke({
    "input": "请在 users 表插入一个用户，名字是 Alice，年龄是 25"
})

print("结果:", result["output"])
