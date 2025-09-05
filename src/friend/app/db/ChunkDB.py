from typing import List

from fastapi import Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from friend.config.DBConfig import get_session
from friend.entity.po.Chunk import Chunk


class ChunkDB:
    def __init__(self,session: AsyncSession):
        self.session = session

    async def insert_list(self,data_list:List[Chunk]):
        """批量插入数据"""
        async with self.session.begin():
            self.session.add_all(data_list)


# 工厂函数
async def create_chunk_db(session: AsyncSession=Depends(get_session))->ChunkDB:
    return ChunkDB(session)