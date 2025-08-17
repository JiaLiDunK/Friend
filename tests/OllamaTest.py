import asyncio
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_ollama import OllamaLLM

from src.friend.agents.node.MilvusNode import MilvusNode

llm = OllamaLLM(model="qwen2.5:7b")

# 提示模板
prompt = ChatPromptTemplate.from_template(
    """根据以下上下文回答问题：
上下文：{context}
问题：{question}
回答："""
)

milvus_node = MilvusNode("test", "ludingji")

async def main(text:str):
    print("开始")
    # 异步调用 search_data
    retriever = await milvus_node.search_data(
        [text],
        ["wenben"],
        10,
        10
    )
    # print("搜索结果:", retriever)
    # 构建 RAG chain
    # 提取文本字段
    # 假设 retriever 是 [[{...}, {...}, ...]]
    flat_hits = retriever[0]  # 解开最外层嵌套
    # 提取 wenben 字段
    context_texts = [hit["entity"]["wenben"] for hit in flat_hits]
    # 拼接成上下文字符串
    context_str = "\n".join(context_texts)
    # print("context_str:", context_str)
    # 包装成一个合法的 Runnable
    context_runnable = RunnableLambda(lambda _: context_str)
    rag_chain = (
        {
            "context": context_runnable,
            "question": RunnablePassthrough()
        }
        | prompt
        | llm
        | StrOutputParser()
    )

    print("开始回答")
    # 异步调用 chain
    result = await rag_chain.ainvoke(text)
    print(result)

# 运行异步主函数
if __name__ == "__main__":
    asyncio.run(main("韦小宝在什么地方有儿子的，儿子叫什么名字"))
