from typing import List

from pymilvus import connections, Collection, MilvusClient, DataType, FieldSchema, CollectionSchema
from loguru import logger
from src.friend.agents.rag.RagNode import RagNode
from src.friend.config.SettingConfig import settings


class MilvusNode:
    def __init__(self,db_name: str,collection_name: str):
        self.client = MilvusClient(
            uri=settings.MILVUS_URL,
            port=settings.MILVUS_PORT,
            db_name=db_name
        )
        self.collection = Collection(collection_name)
        self.rag_node = RagNode()


    async def insert_into_data(self, data):
        """插入数据"""
        self.collection.insert(data)

    async def search_data(self,text_list:List[str],output_fields:List[str],top_k:int=5,nprobe:int=10):
        """搜索数据"""
        embeddings = await self.rag_node.text_to_embedding_documents_bge(text_list)
        search_params = {"metric_type": "COSINE", "params": {"nprobe": nprobe}}
        results = self.collection.search(
            data=embeddings,
            anns_field="vector",
            param=search_params,
            limit=top_k,
            output_fields=output_fields
        )
        return results

    async def search_data_by_ids(self,ids:List[int],output_fields:List[str]):
        """跟id查询数据"""
        return self.collection.query(expr=f"id in {ids}", output_fields=output_fields)
    async def get_all_data_base_name(self):
        """获取所有的数据库的名称"""
        return self.client.list_databases()
    async def get_all_collection_name_by_database_name(self,database_name:str):
        """获取指定数据库下的所有集合名称"""
        self.client.using_database(database_name)
        return self.client.list_collections()
    async def create_database(self,data_base_name:str):
        """创建数据库"""
        if data_base_name in self.client.list_databases():
            logger.info(f"{data_base_name}数据库已经存在")
            return
        await self.create_database(data_base_name=data_base_name)
    async def create_collection(self,data_base_name:str,new_collection_name:str):
        """创建指定数据库中的集合"""
        self.client.using_database(data_base_name)
        # 检查集合是否已经存在
        if new_collection_name in self.client.list_collections():
            logger.info(f"{new_collection_name}集合已经存在")
            return
        # 定义字段
        fields = [
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
            FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=1024),
            FieldSchema(name="content", dtype=DataType.VARCHAR, max_length=4096)
        ]
        # 创建 schema
        schema = CollectionSchema(
            fields=fields,
            description=f"{new_collection_name}的集合",
            enable_dynamic_field=True
        )
        self.client.create_collection(collection_name=new_collection_name, schema=schema)
        logger.info(f"集合 '{new_collection_name}' 创建成功")

