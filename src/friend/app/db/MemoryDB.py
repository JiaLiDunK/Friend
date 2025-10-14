from sqlmodel.ext.asyncio.session import AsyncSession

from src.friend.entity.po.Memory import Memory
from src.friend.config.DBConfig import async_session


class MemoryDB:
    def __init__(self,session:AsyncSession):
        self.session = session

    async def insert_data(self,data:Memory):
        """插入数据"""
        async with self.session.begin():
            self.session.add(data)



# 工厂函数
async def create_memory_db() -> MemoryDB:
    async with async_session() as session:
        return MemoryDB(session)