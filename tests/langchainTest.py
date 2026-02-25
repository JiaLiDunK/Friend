import json
import time

from langchain.agents import create_openai_tools_agent, AgentExecutor
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools import tool
from langchain_community.chat_models.tongyi import ChatTongyi
from pydantic import BaseModel


# 定义一个简单工具
@tool
def insert_record_two(table: str, values: dict) -> str:
    """1往指定表插入一条数据"""
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    return f"成功插入 {values} 到 {table}"
@tool
def insert_record_one(table: str, values: dict) -> str:
    """往指定表插入一条数据"""
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    return f"2成功插入 {values} 到 {table}"
tools = [insert_record_one,insert_record_two]

# 选择模型
llm = ChatTongyi(model="qwen-plus", api_key="sk-")

# 定义 prompt
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个智能助手，可以调用工具完成任务,必须同时调用两个工具。"),
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

# 定义一个数据模型（用于把JSON转成对象）
class Book(BaseModel):
    tittle: str
    author: str
    year: int
    genre: str

# 初始化 LLM
llm = ChatTongyi(model="qwen-plus", api_key="sk-")

# 定义提示模板
prompt = ChatPromptTemplate.from_template("""
请生成一个书籍信息的JSON，包含以下字段：
tittle（书名）、author（作者）、year（出版年份）、genre（类型）。
只返回JSON格式。
""")

# 生成内容
response = llm.invoke(prompt.format())

# 输出原始字符串
print("🔹 LLM返回内容：")
print(response.content)

# 解析成JSON对象
data = json.loads(response.content)

# 转换成Python对象
book = Book(**data)

# 打印结果
print("\n🔹 转换为对象：")
print(book)
print(f"书名：{book.title}，作者：{book.author}")
