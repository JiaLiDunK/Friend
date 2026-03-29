import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import List, Optional

from loguru import logger
from pymilvus import MilvusClient, FieldSchema, CollectionSchema, DataType
from pymilvus.milvus_client import IndexParams

from src.friend.agents.node.RagNode import RagNode, get_rag_node
from src.friend.app.db.KnowledgeBaseDB import create_knowledge_base_db, KnowledgeBaseDB, \
    create_knowledge_base_db_by_load
from src.friend.config.SettingConfig import settings
from src.friend.entity.ai.AIResponseMessage import QuestionId
from src.friend.entity.ai.MilvusResponse import SearchContent, SelectContent


class MilvusNode:
    _executor = ThreadPoolExecutor(max_workers=10)  # 并发执行同步方法
    def __init__(self,knowledge_base_db:KnowledgeBaseDB,rag_node:RagNode, db_name: str, collection_name: str):
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
        self.rag_node = rag_node
        # 检查并创建集合
        if not self.client.has_collection(collection_name):
            self._create_default_collection(collection_name)
        logger.success(f"MilvusNode 已连接: DB={db_name}, Collection={collection_name}")
    @classmethod
    async def create(cls):
        knowledge_base_db = await create_knowledge_base_db()
        rag_node = await get_rag_node()
        return cls(knowledge_base_db,rag_node,db_name="default",collection_name="default")

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


    async def search_data_get_list(self,search_data:QuestionId,top_k: int = 5,
        nprobe: int = 10)->List[SelectContent]:
        """生成的问题去指定的知识库中查询"""
        embedding = await self.rag_node.text_to_embedding_query_bge(search_data.question)
        search_params = {"metric_type": "L2", "params": {"nprobe": nprobe}}
        # 切换知识库
        self.client.using_database(search_data.data_base)
        self.client.load_collection(search_data.collection)
        # 检索
        data_list = await self._run_async(
            self.client.search,
            collection_name=search_data.collection,
            data=[embedding],
            anns_field="vector",
            search_params=search_params,
            limit=top_k,
            output_fields=["content"],
        )
        milvus_list = [SearchContent(**item) for item in data_list[0]]
        # 过滤掉相似度低的数据
        milvus_list = [item for item in milvus_list if item.distance >= 0.65]
        if len(milvus_list) == 0:
            return []
        result_list: List[SelectContent] = []
        for item in milvus_list:
            current_id = item.id
            context_text = item.entity.content
            result_list.append(
                SelectContent(id=current_id,
                content=context_text.strip(),
                distance=item.distance)
            )
        result_list.sort()
        return result_list

    async def search_know_base(self,search_data:QuestionId,top_k: int = 5,
        nprobe: int = 10)->List[SelectContent]:
        """生成的问题去指定的知识库中查询"""
        embedding = await self.rag_node.text_to_embedding_query_bge(search_data.question)
        search_params = {"metric_type": "L2", "params": {"nprobe": nprobe}}
        # 切换知识库
        self.client.using_database(search_data.data_base)
        self.client.load_collection(search_data.collection)
        # 检索
        data_list = await self._run_async(
            self.client.search,
            collection_name=search_data.collection,
            data=[embedding],
            anns_field="vector",
            search_params=search_params,
            limit=top_k,
            output_fields=["content"],
        )
        milvus_list = [SearchContent(**item) for item in data_list[0]]
        # 过滤掉相似度低的数据
        milvus_list = [item for item in milvus_list if item.distance >= 0.65]
        if len(milvus_list) == 0:
            return []
        # 下述是根据id获取前后文的内容,暂时不需要
        id_list = [item.id for item in milvus_list]
        context_ids = list(set([i for id_ in id_list for i in (id_ - 1, id_, id_ + 1) if i >= 0]))
        id_expr = f"id in {context_ids}"  # 生成 Milvus 查询条件
        response_list = await self._run_async(
            self.client.query,
            collection_name=search_data.collection,
            filter=id_expr,
            output_fields=["content"],
        )
        all_docs = {item["id"]: item["content"] for item in response_list}
        result_list:List[SelectContent] = []
        for item in milvus_list:
            current_id = item.id
            context_text = (
                    all_docs.get(current_id - 1, "") +
                    all_docs.get(current_id, "") +
                    all_docs.get(current_id + 1, "")
            )
            result_list.append(
                SelectContent(id=current_id,
                content=context_text.strip(),
                distance=item.distance)
            )
        result_list.sort()
        return result_list

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


    async def create_collection_by_qa(self, data_base_name: str, new_collection_name: str):
        """在指定数据库中创建集合"""
        self.client.using_database(data_base_name)
        existing = await self._run_async(self.client.list_collections)
        if new_collection_name in existing:
            logger.info(f"集合 '{new_collection_name}' 已存在")
            return
        fields = [
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
            FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=512),
            FieldSchema(name="content", dtype=DataType.VARCHAR, max_length=4096),
            FieldSchema(name="qa_id", dtype=DataType.INT64),
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
            knowledge_base_db = await create_knowledge_base_db_by_load()
            rag_node = await get_rag_node()
            _milvus_node_instance = MilvusNode(knowledge_base_db=knowledge_base_db,rag_node=rag_node,db_name=db_name, collection_name=collection_name)
            logger.info(f"MilvusNode 实例已创建：DB={db_name}, Collection={collection_name}")
        return _milvus_node_instance
