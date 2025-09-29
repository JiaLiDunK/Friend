from typing import List, Tuple

from langchain_core.tools import tool

from src.friend.entity.po.BookVectors import BookVectors
from src.friend.entity.po.KnowledgeBase import KnowledgeBase
from src.friend.app.db.BooksDB import create_books_db
from src.friend.app.db.KnowledgeBaseDB import create_knowledge_base_db
from loguru import logger

class DataBaseTools:
    def __init__(self,knowledge_base_db,books_db):
        self.knowledge_base_db = knowledge_base_db
        self.books_db = books_db
    @classmethod
    async def create(cls):
        knowledge_base_db = await create_knowledge_base_db()
        books_db = await create_books_db()
        return cls(knowledge_base_db,books_db)

    @staticmethod
    @tool
    async def insert_knowledge_base(
    self,
    data_base: str,
    collection: str,
    data_base_remark: str,
    collection_remark: str,
    type_id: int):
        """是往knowledge_base表中插入数据"""
        logger.info(f"agent插入知识库:{data_base}//{collection}//{data_base_remark}//{collection_remark}//{type_id}")
        self.knowledge_base_db.insert_data(KnowledgeBase(data_base=data_base,collection=collection,data_base_remark=data_base_remark,collection_remark=collection_remark,type_id=type_id))
        return "插入成功"

    @staticmethod
    @tool
    async def update_book_vectors(self,data: List[Tuple[int, int]]) -> str:
        """更新 book_vectors 表中的数据。每个元素为 (id, knowledge_base_id)"""
        for id_, kb_id in data:
            logger.info(f"agent更新数据 id={id_}, knowledge_base_id={kb_id}")
            # 在这里写数据库更新逻辑
            self.books_db.update_data(BookVectors(id=id_, knowledge_base_id=kb_id))
        return "更新成功"