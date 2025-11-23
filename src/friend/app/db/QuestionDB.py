from sqlmodel.ext.asyncio.session import AsyncSession

from src.friend.config.DBConfig import async_session
from src.friend.entity.po.Question import Question


class QuestionDB:
    def __init__(self,session: AsyncSession):
        self.session = session
    async def __aenter__(self):
        self.session = async_session()
        await self.session.__aenter__()
        return QuestionDB(self.session)
    async def __aexit__(self, exc_type, exc, tb):
        await self.session.__aexit__(exc_type, exc, tb)
    async def insert_data(self,data:Question):
        """添加单个数据"""
        self.session.add(data)
        await self.session.commit()

# 工厂函数
async def create_question_db():
    async with async_session() as session:
        yield QuestionDB(session)
async def create_question_db_by_load():
    async with async_session() as session:
        return QuestionDB(session)