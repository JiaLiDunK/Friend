from fastapi.params import Depends
from sqlalchemy import func
from sqlmodel import select,update
from sqlmodel.ext.asyncio.session import AsyncSession

from src.friend.config.DBConfig import get_session
from src.friend.entity.po.BookVectors import BookVectors
from src.friend.entity.vo.QueryTable import QueryTable


class BookVectorsDB:
    def __init__(self,session: AsyncSession):
        self.session = session

    async def insert_data(self,data:BookVectors):
        """插入书籍记录"""
        async with self.session.begin():
            self.session.add(data)
    async def update_data(self,data:BookVectors):
        """更新书籍记录"""
        async with self.session.begin():
            statement = update(BookVectors).where(BookVectors.id==data.id).values(uuid=data.uuid,type_id=data.type_id,knowledge_base_id=data.knowledge_base_id)
            await self.session.exec(statement)







# 工厂函数
async def create_book_vectors_db(session: AsyncSession=Depends(get_session)) -> BookVectorsDB:
    return BookVectorsDB(session)