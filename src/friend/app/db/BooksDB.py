from sqlmodel.ext.asyncio.session import AsyncSession

from src.friend.config.DBConfig import async_session
from src.friend.entity.po.Books import Books


class BooksDB:
    def __init__(self,session: AsyncSession):
        self.session = session

    async def insert_data(self,data:Books):
        """插入书籍"""
        async with self.session.begin():
            self.session.add(data)




# 工厂函数（业务内部调用用这个）
async def create_books_db() -> BooksDB:
    async with async_session() as session:
        return BooksDB(session)