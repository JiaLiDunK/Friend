import asyncio

from src.friend.agents.node.RagNode import RagNode
from pymilvus import connections, utility, FieldSchema, CollectionSchema, DataType, Collection


async def main():
    # 连接 Milvus 数据库
    # connections.connect(host="localhost", port="19530", db_name="test")
    # 初始化 RagNode
    node = RagNode()
    # 查看集合列表
    # print(utility.list_collections())
    #
    #
    # # 定义集合 schema（如果你只是加载已有集合，这部分可以省略）
    # fields2 = [
    #     FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
    #     FieldSchema(name="member", dtype=DataType.FLOAT_VECTOR, dim=1024),
    #     FieldSchema(name="text", dtype=DataType.INT16)
    # ]
    # schema2 = CollectionSchema(fields2, description="向量集合示例")
    #
    # # 加载已存在的集合
    # collection2 = Collection("test")

    # 文本数据
    test = ['why does lin yujing insist on living in his ancestral alleyway despite having houses in major cities',
            "what is the reason behind xiaowei staying in yuling instead of moving to beijing with her grandparents",
            'why does lin yujing insist on living in his ancestral alleyway despite having houses in major cities',
            "what is the reason behind xiaowei staying in yuling instead of moving to beijing with her grandparents"
            ]

    # 异步获取嵌入向量
    embeddings = await node.text_to_embedding_documents_bge(test)
    print(len(embeddings[0]))
    # 其他字段数据
    # tests = [9, 9]
    #
    # # 构造插入数据（注意顺序要与 schema 对应）
    # data = [
    #     embeddings,  # 对应 "member"
    #     tests        # 对应 "text"
    # ]
    #
    # print(embeddings)
    # print(test)

    # # 插入数据
    # collection2.insert(data)

    print("结束")

async def main_search():
    print("开始")
    # 初始化 RagNode
    node = RagNode()
    print("初始化完成")
    # 连接 Milvus 数据库
    connections.connect(host="localhost", port="19530", db_name="test")
    collection = Collection("ludingji")
    print("连接成功")
    # 文本数据
    test = ['韦小宝在妓院里面跟七个女人上床']
    # 异步获取嵌入向量
    embeddings = await node.text_to_embedding_documents_bge(test)
    # 查找最相似的5个结果
    top_k = 5
    search_params = {"metric_type": "COSINE", "params": {"nprobe": 10}}
    print("开始查找")
    results = collection.search(
        data=embeddings,
        anns_field="vector",
        param=search_params,
        limit=top_k,
        output_fields = ["wenben"]
    )
    print("展示查找结果")
    print(results[0][0]['entity']['wenben'])
    collection.release()

if __name__ == '__main__':
    asyncio.run(main())
    print("结束")