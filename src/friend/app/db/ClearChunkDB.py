from typing import List

from sqlmodel.ext.asyncio.session import AsyncSession

from src.friend.config.DBConfig import async_session
from src.friend.entity.po.ClearChunk import ClearChunk


class ClearChunkDB:
    def __init__(self,session: AsyncSession):
        self.session = session
    async def __aenter__(self):
        self.session = async_session()
        await self.session.__aenter__()
        return ClearChunkDB(self.session)
    async def __aexit__(self, exc_type, exc, tb):
        await self.session.__aexit__(exc_type, exc, tb)

    async def inset_data_one(self,data:ClearChunk):
        """插入数据"""
        self.session.add(data)
        await self.session.commit()
    async def insert_data_list(self,data:List[ClearChunk]):
        """批量插入"""
        self.session.add_all(data)
        await self.session.commit()

# 工厂函数
async def create_clear_chunk_db():
    async with async_session() as session:
        yield ClearChunkDB(session)
async def create_clear_chunk_db_by_load():
    async with async_session() as session:
        return ClearChunkDB(session)