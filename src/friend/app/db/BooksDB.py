from fastapi.params import Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from src.friend.config.DBConfig import get_session
from src.friend.entity.po.Books import Books


class BooksDB:
    def __init__(self,session: AsyncSession):
        self.session = session
    async def insert_data(self,data:Books):
        """插入书籍"""
        async with self.session.begin():
            self.session.add(data)




# 工厂函数
async def create_books_db(session: AsyncSession=Depends(get_session))->BooksDB:
    return BooksDB(session)