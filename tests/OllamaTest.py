import asyncio

from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_ollama import OllamaLLM

from src.friend.agents.node.MilvusNode import MilvusNode

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
        - 页码（例如：567、568）
        - URL 链接（例如：http://xxx.com）
        - 出版社或版权信息（例如：Copyright©2018 黑马程序员、感恩于心 回报于行）
        - 解析错误导致的重复或乱码
        
        你的任务是：
        1. 删除这些无关内容。
        2. 保留清晰、连贯的正文，不改变原文的语义。
        3. 如果正文中有换行被错误切断，请适当合并为通顺的段落。
        4. 输出干净的文本，不要添加任何额外说明。
        
        示例输入：
        "发顺序和触发条件，每个任务可以由一个或多个软件系统完成，还可以由一个或一组人完成，还可以由一个或多个人
        与软件系统协作完。
        567
        http://www.itheima.com Copyright©2018 黑马程序员"
        
        示例输出：
        "发顺序和触发条件，每个任务可以由一个或多个软件系统完成，还可以由一个或一组人完成，还可以由一个或多个人与软件系统协作完。"
        """
    )
    user = HumanMessage("""
208
http://www.itheima.com Copyright©2018 黑马程序员
感恩于心，回报于行。 面试宝典系列-Java
pred = p;
}
return false;
}
✓ contains操作"
"感恩于心，回报于行。 面试宝典系列-Java
pred = p;
}
return false;
}
✓ contains操作
判断队列里面是否含有指定对象，由于是遍历整个队列，所以类似size 不是那么精确，有可能调用该方法
时候元素还在队列里面，但是遍历过程中才把该元素删除了，那么就会返回false.
public boolean contains(Object o) {
if (o == null) return false;
for (Node<E> p = first(); p != null; p = succ(p)) {
E item = p.item;
if (item != null && o.equals(item))
return true;
}
return false;
}
ConcurrentLinkedQuere的offer方法有意思的问题
offer中有个 判断 t != (t = tail）假如 t=node1;tail=node2;并且node1!=node2那么这个判断是true还
是false那，答案是true，这个判断是看当前t是不是和tail相等，相等则返回true否者为false，但是无论
结果是啥执行后t的值都是tail。
下面从字节码来分析下为啥。
• 一个例子
public static void main(String[] args) {"
"结果是啥执行后t的值都是tail。
下面从字节码来分析下为啥。
• 一个例子
public static void main(String[] args) {
int t = 2;
int tail = 3;
System.out.println(t != (t = tail));
}
结果为：true
• 字节码文件
C:\\Users\\Simple\\Desktop\\TeacherCode\\Crm_Test\\build\\classes\\com\\itheima\\crm\\util>javap -c Test001
警告: 二进制文件Test001包含com.itheima.crm.util.Test001
Compiled from ""Test001.java""
public class com.itheima.crm.util.Test001 {
209
http://www.itheima.com Copyright©2018 黑马程序员
感恩于心，回报于行。 面试宝典系列-Java
public com.itheima.crm.util.Test001();
Code:
0: aload_0
1: invokespecial #8 // Method java/lang/Object.""<init>"":()V
4: return"
"Code:
0: aload_0
1: invokespecial #8 // Method java/lang/Object.""<init>"":()V
4: return
public static void main(java.lang.String[]);
Code:
0: iconst_2
1: istore_1
2: iconst_3
3: istore_2
4: getstatic #16 // Field java/lang/System.out:Ljava/io/PrintStream;
7: iload_1
8: iload_2
9: dup
10: istore_1
11: if_icmpeq 18
14: iconst_1
15: goto 19
18: iconst_0
19: invokevirtual #22 // Method java/io/PrintStream.println:(Z)V
22: return
}
我们从上面标黄的字节码文件中分析
一开始栈为空：
栈
• 第0行指令作用是把值2入栈栈顶元素为2
210
http://www.itheima.com Copyright©2018 黑马程序员
感恩于心，回报于行。 面试宝典系列-Java
    """)
    prompt = [
        message,
        user
    ]
    result = llm.invoke(prompt)
    print(result)
