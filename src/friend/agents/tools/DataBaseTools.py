from langchain_core.tools import tool

from src.friend.entity.po.BookVectors import BookVectors
from src.friend.entity.po.KnowledgeBase import KnowledgeBase
from src.friend.app.db.BooksDB import create_books_db
from src.friend.app.db.KnowledgeBaseDB import create_knowledge_base_db


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
        await self.knowledge_base_db.insert_data(data)
        return "插入成功"
    @tool(args_schema=BookVectors)
    async def insert_book_vectors(self):
        """是往book_vectors表中插入数据"""
        pass