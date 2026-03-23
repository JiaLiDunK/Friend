from typing import List

from sqlmodel.ext.asyncio.session import AsyncSession

from src.friend.config.DBConfig import async_session
from src.friend.entity.po.Answer import Answer


class AnswerDB:
    def __init__(self,session: AsyncSession):
        self.session = session
    async def insert_data_list(self,data:List[Answer]):
        """批量插入数据"""
        self.session.add_all(data)
        await self.session.commit()

# 工厂函数
async def create_answer_db():
    async with async_session() as session:
        yield AnswerDB(session)
