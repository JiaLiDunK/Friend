from typing import List

from sqlmodel.ext.asyncio.session import AsyncSession

from src.friend.config.DBConfig import async_session
from src.friend.entity.po.Chunk import Chunk


class ChunkDB:
    def __init__(self,session: AsyncSession):
        self.session = session

    async def insert_list(self,data_list:List[Chunk]):
        """批量插入数据"""
        async with self.session.begin():
            self.session.add_all(data_list)

# 工厂函数（业务内部调用用这个）
async def create_chunk_db() -> ChunkDB:
    async with async_session() as session:
        return ChunkDB(session)
