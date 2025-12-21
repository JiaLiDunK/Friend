from typing import List

from sqlmodel.ext.asyncio.session import AsyncSession

from src.friend.config.DBConfig import async_session
from src.friend.entity.po.QApairs import QApairs


class QApairsDB:
    def __init__(self,session: AsyncSession):
        self.session = session
    async def __aenter__(self):
        self.session = async_session()
        await self.session.__aenter__()
        return QApairsDB(self.session)

    async def __aexit__(self, exc_type, exc, tb):
        await self.session.__aexit__(exc_type, exc, tb)
    async def insert_data(self,data:QApairs):
        """添加单个数据"""
        self.session.add(data)
        await self.session.commit()
    async def del_data(self,data:QApairs):
        """删除单个数据"""
        await self.session.delete(data)
        await self.session.commit()
    async def insert_list(self,data_list:List[QApairs]):
        """批量插入数据"""
        self.session.add_all(data_list)
        await self.session.commit()


# 工厂函数
async def create_qa_pairs_db():
    async with async_session() as session:
        yield QApairsDB(session)
async def create_qa_pairs_load():
    async with async_session() as session:
        return QApairsDB(session)