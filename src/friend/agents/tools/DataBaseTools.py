from typing import List, Tuple
from src.friend.entity.po.BookVectors import BookVectors
from src.friend.entity.po.KnowledgeBase import KnowledgeBase
from src.friend.app.db.BooksDB import create_books_db
from src.friend.app.db.KnowledgeBaseDB import create_knowledge_base_db
from loguru import logger
from langchain.tools import StructuredTool

class DataBaseTools:
    def __init__(self, knowledge_base_db, books_db):
        self.knowledge_base_db = knowledge_base_db
        self.books_db = books_db

    @classmethod
    async def create(cls):
        """异步创建 DataBaseTools"""
        knowledge_base_db = await create_knowledge_base_db()
        books_db = await create_books_db()
        return cls(knowledge_base_db, books_db)

    async def insert_knowledge_base(
        self,
        data_base: str,
        collection: str,
        data_base_remark: str,
        collection_remark: str,
        type_id: int
    ) -> str:
        """往 knowledge_base 表中插入一条数据"""
        logger.info(
            f"agent插入知识库: {data_base}//{collection}//{data_base_remark}//{collection_remark}//{type_id}"
        )
        await self.knowledge_base_db.insert_data(
            KnowledgeBase(
                id=None,
                data_base=data_base,
                collection=collection,
                data_base_remark=data_base_remark,
                collection_remark=collection_remark,
                type_id=type_id
            )
        )
        return "插入成功"

    async def update_book_vectors(self, data: List[Tuple[int, int]]) -> str:
        """修改 book_vectors 中的数据,数据格式是[(id, knowledge_base_id), ...]"""
        for id_, kb_id in data:
            logger.info(f"agent更新数据 id={id_}, knowledge_base_id={kb_id}")
            await self.books_db.update_data_only_id(
                BookVectors(id=id_, knowledge_base_id=kb_id)
            )
        return "更新成功"

    def get_tools(self):
        """注册为 LangChain 工具"""
        return [
            StructuredTool.from_function(
                coroutine=self.insert_knowledge_base,   # 异步函数
                name="insert_knowledge_base",
                description="往 knowledge_base 表插入数据"
            ),
            StructuredTool.from_function(
                coroutine=self.update_book_vectors,     # 异步函数
                name="update_book_vectors",
                description="更新 book_vectors 表中的 knowledge_base_id"
            ),
        ]