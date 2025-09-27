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

    @tool(args_schema=KnowledgeBase)
    async def insert_knowledge_base(self,data:KnowledgeBase):
        """是往knowledge_base表中插入数据"""
        logger.info(f"插入知识库:{data}")
        return "插入成功"

    @tool
    async def update_book_vectors(data: List[Tuple[int, int]]) -> str:
        """更新 book_vectors 表中的数据。每个元素为 (id, knowledge_base_id)"""
        for id_, kb_id in data:
            logger.info(f"更新数据 id={id_}, knowledge_base_id={kb_id}")
            # 在这里写数据库更新逻辑
        return "更新成功"