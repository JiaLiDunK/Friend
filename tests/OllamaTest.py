from langchain_core.messages import SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import OllamaLLM
from langchain_community.callbacks.manager import get_openai_callback
llm = OllamaLLM(
    model="qwen3:8b",
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
        你是一个文本清洗助手。我会给你一段从 PDF 解析出来的文字，其中可能包含以下无关内容：
        """
    )

    prompt = [
        message,
    ]
    from langchain_ollama.chat_models import ChatOllama
    from langchain.schema import SystemMessage

    llm = ChatOllama(model="qwen3:8b", reasoning = True)

    message = SystemMessage("你是一个文本清洗助手。帮我去掉无关信息。")

    # 执行
    result = llm.invoke([message])

    print("====结果=====")
    print(result.content)

    # 打印元信息
    print("====元数据=====")
    print(result.response_metadata)
