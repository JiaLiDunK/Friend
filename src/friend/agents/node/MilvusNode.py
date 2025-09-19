from typing import List

from pymilvus import connections, Collection

from src.friend.agents.rag.RagNode import RagNode
from src.friend.config.SettingConfig import settings


class MilvusNode:
    def __init__(self,db_name: str,collection_name: str):
        connections.connect(host=settings.MILVUS_URL, port=settings.MILVUS_PORT, db_name=db_name)
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