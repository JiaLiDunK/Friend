import asyncio
from typing import List, Optional

from langchain_ollama import OllamaEmbeddings
from loguru import logger


class RagNode:
    """
    RagNode 负责文本向量化 (embedding)，支持 query 与 documents 两种模式。
    默认使用 Ollama 的 bge-m3 模型。
    """

    def __init__(self, model_name: str = "bge-m3:latest"):
        self.model_name = model_name
        self._bge_m3: Optional[OllamaEmbeddings] = None
        self._lock = asyncio.Lock()  # 防止多协程同时初始化

    async def _ensure_model_loaded(self):
        """确保模型已初始化（延迟加载）"""
        if self._bge_m3 is None:
            async with self._lock:
                if self._bge_m3 is None:
                    logger.info(f"正在加载 Embedding 模型：{self.model_name}")
                    # OllamaEmbeddings 是同步对象，所以直接创建
                    self._bge_m3 = OllamaEmbeddings(model=self.model_name)
                    logger.success(f"模型 {self.model_name} 加载完成")

    async def text_to_embedding_documents_bge(self, texts: List[str]):
        """
        将文本列表转为向量列表
        """
        await self._ensure_model_loaded()
        loop = asyncio.get_running_loop()
        # embed_documents 是同步函数 → 转线程池执行，防止阻塞事件循环
        return await loop.run_in_executor(None, lambda: self._bge_m3.embed_documents(texts))

    async def text_to_embedding_query_bge(self, text: str):
        """
        将单个查询文本转为向量
        """
        await self._ensure_model_loaded()
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, lambda: self._bge_m3.embed_query(text))

    @classmethod
    async def create(cls, model_name: str = "bge-m3"):
        """
        工厂方法，保持与其他 Node 类一致
        """
        instance = cls(model_name)
        await instance._ensure_model_loaded()
        return instance

async def get_rag_node() -> RagNode:
    """获取全局 RagNode 单例"""
    if not hasattr(get_rag_node, "instance"):
        get_rag_node.instance = await RagNode.create()
    return get_rag_node.instance
