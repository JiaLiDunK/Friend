from litellm.proxy.proxy_server import embeddings
from pymilvus.milvus_client import IndexParams

from friend.entity.ai.AIResponseMessage import AIResponseMessage
from src.friend.app.db.KnowledgeBaseDB import create_knowledge_base_db
from src.friend.agents.node.RagNode import RagNode
from src.friend.config.SettingConfig import settings

from typing import List, Optional
from pymilvus import MilvusClient, FieldSchema, CollectionSchema, DataType, Collection
from loguru import logger
import asyncio
from concurrent.futures import ThreadPoolExecutor


class MilvusNode:
    _executor = ThreadPoolExecutor(max_workers=4)  # 并发执行同步方法
    def __init__(self,knowledge_base_db, db_name: str, collection_name: str):
        self.db_name = db_name
        self.collection_name = collection_name
        self.knowledge_base_db = knowledge_base_db
        #修正连接 URI，确保符合新版要求
        uri = settings.MILVUS_URL
        if not uri.startswith(("tcp://", "http://", "https://", "unix://")):
            uri = f"tcp://{uri}:{settings.MILVUS_PORT}"
        self.client = MilvusClient(uri=uri, db_name=db_name)
        # 切换数据库
        self.client.using_database(db_name)
        self.rag_node = RagNode()
        # 检查并创建集合
        if not self.client.has_collection(collection_name):
            self._create_default_collection(collection_name)
        logger.success(f"MilvusNode 已连接: DB={db_name}, Collection={collection_name}")
    @classmethod
    async def create(cls):
        knowledge_base_db = await create_knowledge_base_db()
        return cls(knowledge_base_db,db_name="default",collection_name="default")

    def _create_default_collection(self, collection_name: str):
        """内部函数：确保默认集合存在"""
        fields = [
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
            FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=1024),
            FieldSchema(name="content", dtype=DataType.VARCHAR, max_length=4096),
        ]
        schema = CollectionSchema(fields=fields, enable_dynamic_field=True)
        self.client.create_collection(collection_name=collection_name, schema=schema)
        logger.info(f"默认集合 {collection_name} 已创建")

    # ------------------------- 工具函数 -------------------------
    async def _run_async(self, func, *args, **kwargs):
        """在异步环境中运行同步 Milvus 方法"""
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(self._executor, lambda: func(*args, **kwargs))

    # ------------------------- 数据操作 -------------------------
    async def insert_into_data(self, data,data_base_name,collection_name):
        """插入数据"""
        logger.info(f"看看有没有进入这块{data_base_name}====={collection_name}")
        def sync_insert():
            self.client.using_database(data_base_name)
            logger.info(f"切换了数据库 {data_base_name}")
            return self.client.insert(collection_name, data)

        return await self._run_async(sync_insert)

    async def search_data(
        self,
        text_list: List[str],
        output_fields: List[str],
        top_k: int = 5,
        nprobe: int = 10
    ):
        """向量搜索"""
        embeddings = await self.rag_node.text_to_embedding_documents_bge(text_list)
        search_params = {"metric_type": "COSINE", "params": {"nprobe": nprobe}}
        return await self._run_async(
            self.client.search,
            collection_name=self.collection_name,
            data=embeddings,
            anns_field="vector",
            search_params=search_params,
            limit=top_k,
            output_fields=output_fields,
        )

    async def search_data_by_ids(self, ids: List[int], output_fields: List[str]):
        """根据 ID 查询数据"""
        expr = f"id in {ids}"
        return await self._run_async(
            self.client.query,
            collection_name=self.collection_name,
            expr=expr,
            output_fields=output_fields
        )
    async def search_data_get_list(self,search_data:AIResponseMessage,top_k: int = 5,
        nprobe: int = 10):
        """生成的问题去指定的知识库中查询"""
        knowledge_base = await self.knowledge_base_db.get_data_by_id(search_data.knowledge_base_id)
        embedding = await self.rag_node.text_to_embedding_query_bge(AIResponseMessage.message)
        search_params = {"metric_type": "COSINE", "params": {"nprobe": nprobe}}
        # 切换知识库
        self.client.using_database(knowledge_base.data_base)
        data_list = await self._run_async(
            self.client.search,
            collection_name=knowledge_base.collection,
            data=embedding,
            anns_field="vector",
            search_params=search_params,
            limit=top_k,
            output_fields=["content"],
        )
        # 还需要的是根据id获取前后文的内容

    # ------------------------- 数据库与集合管理 -------------------------
    async def get_all_data_base_name(self):
        """获取所有数据库名称"""
        return await self._run_async(self.client.list_databases)

    async def get_all_collection_name_by_database_name(self, database_name: str):
        """获取指定数据库下所有集合"""
        self.client.using_database(database_name)
        return await self._run_async(self.client.list_collections)

    async def create_database(self, data_base_name: str):
        """创建数据库"""
        existing_dbs = await self._run_async(self.client.list_databases)
        if data_base_name in existing_dbs:
            logger.info(f"数据库 '{data_base_name}' 已存在")
            return
        await self._run_async(self.client.create_database, data_base_name)
        logger.success(f"数据库 '{data_base_name}' 创建成功")

    async def create_collection(self, data_base_name: str, new_collection_name: str):
        """在指定数据库中创建集合"""
        self.client.using_database(data_base_name)
        existing = await self._run_async(self.client.list_collections)
        if new_collection_name in existing:
            logger.info(f"集合 '{new_collection_name}' 已存在")
            return
        fields = [
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
            FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=1024),
            FieldSchema(name="content", dtype=DataType.VARCHAR, max_length=4096),
        ]
        schema = CollectionSchema(fields=fields, enable_dynamic_field=True)
        await self._run_async(self.client.create_collection, new_collection_name, schema=schema)
        logger.success(f"集合 '{new_collection_name}' 创建成功")
        #创建索引
        index_params = IndexParams()
        index_params.add_index(
            field_name="vector",
            index_type="HNSW",
            metric_type="L2",
            params={"M": 8, "efConstruction": 64}
        )
        await self._run_async(
            self.client.create_index,
            collection_name=new_collection_name,
            index_params=index_params
        )

# ------------------------- 单例管理 -------------------------
_milvus_node_instance: Optional[MilvusNode] = None
_milvus_lock = asyncio.Lock()


async def create_milvus_node(db_name: str = "default", collection_name: str = "default") -> MilvusNode:
    """异步单例，获取 MilvusNode 实例"""
    global _milvus_node_instance
    async with _milvus_lock:
        if _milvus_node_instance is None:
            _milvus_node_instance = MilvusNode(db_name, collection_name)
            logger.info(f"MilvusNode 实例已创建：DB={db_name}, Collection={collection_name}")
        return _milvus_node_instance
