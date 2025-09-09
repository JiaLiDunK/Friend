from fastapi.params import Depends
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from friend.entity.po.VectorRecord import VectorRecord
from src.friend.config.DBConfig import get_session

class VectorRecordDB:
    def __init__(self,session: AsyncSession):
        self.session = session

    async def insert_data(self,data:VectorRecord):
        """插入书籍记录"""
        async with self.session.begin():
            self.session.add(data)

    async def get_by_tittle(self,tittle:str):
        """查询书籍名是否已经导入"""
        async with self.session.begin():
            statement = select(VectorRecord).where(VectorRecord.tittle==tittle)
            result = await self.session.exec(statement)
            return result.one_or_none()






# 工厂函数
async def create_vector_record_db(session: AsyncSession=Depends(get_session)) -> VectorRecordDB:
    return VectorRecordDB(session)