import asyncio

from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_ollama import OllamaLLM

from src.friend.agents.node.MilvusNode import MilvusNode

llm = OllamaLLM(
    model="huihui_ai/qwen3-abliterated:8b",
    reasoning = True #这个是关闭思考模型的回复
)

# 提示模板
prompt = ChatPromptTemplate.from_template(
    """根据以下上下文回答问题：
上下文：{context}
问题：{question}
回答："""
)

# milvus_node = MilvusNode("novel", "ppyx")
#
# async def main(text:str):
#     print("开始")
#     # 异步调用 search_data
#     retriever = await milvus_node.search_data(
#         [text],
#         ["content"],
#         10,
#         10
#     )
#     # print("搜索结果:", retriever)
#     # 构建 RAG chain
#     # 提取文本字段
#     # 假设 retriever 是 [[{...}, {...}, ...]]
#     flat_hits = retriever[0]  # 解开最外层嵌套
#     print(flat_hits)
#     # 提取 wenben 字段
#     context_texts = [hit["entity"]["content"] for hit in flat_hits]
#     # 拼接成上下文字符串
#     context_str = "\n".join(context_texts)
#     # print("context_str:", context_str)
#     # 包装成一个合法的 Runnable
#     context_runnable = RunnableLambda(lambda _: context_str)
#     rag_chain = (
#         {
#             "context": context_runnable,
#             "question": RunnablePassthrough()
#         }
#         | prompt
#         | llm
#         | StrOutputParser()
#     )
#
#     print("开始回答")
#     # 异步调用 chain
#     result = await rag_chain.ainvoke(text)
#     print(result)
# async def search_id(text:str):
#     print("开始")
#     # 异步调用 search_data
#     retriever = await milvus_node.search_data(
#         [text],
#         ["content","id"],
#         5,
#         10
#     )
#     # print("搜索结果:", retriever)
#     # 构建 RAG chain
#     # 提取文本字段
#     # 假设 retriever 是 [[{...}, {...}, ...]]
#     flat_hits = retriever[0]  # 解开最外层嵌套
#     # print(flat_hits)
#     # 提取 wenben 字段
#     context_ids = [hit["entity"]["id"] for hit in flat_hits]
#     select_ids = []
#     for i in context_ids:
#         select_ids.append(i+1)
#         select_ids.append(i-1)
#     print(select_ids)
#     await get_by_ids(select_ids,text)
#
# async def get_by_ids(ids:list[int],text:str):
#     response = await milvus_node.search_data_by_ids(ids,['content'])
#     context_texts = [hit["content"] for hit in response]
#     context_str = "\n".join(context_texts)
#     # print("context_str:", context_str)
#     # 包装成一个合法的 Runnable
#     context_runnable = RunnableLambda(lambda _: context_str)
#     rag_chain = (
#             {
#                 "context": context_runnable,
#                 "question": RunnablePassthrough()
#             }
#             | prompt
#             | llm
#             | StrOutputParser()
#     )
#
#     print("开始回答")
#     # 异步调用 chain
#     result = await rag_chain.ainvoke(text)
#     print(result)
# 运行异步主函数
if __name__ == "__main__":
    # asyncio.run(search_id(""))
    # 提示模板
    message = SystemMessage(
        """
        判断下面的内容有没有保存的必要，如果有必要，就返回1,没有必要，就返回2
        """
    )
    user = HumanMessage("贷方发生发射点发大水·")
    prompt = [
        message,
        user
    ]
    result = llm.invoke(prompt)
    print(result)
