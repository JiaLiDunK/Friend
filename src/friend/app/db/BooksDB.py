from sqlalchemy import func, update
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.friend.config.DBConfig import async_session
from src.friend.entity.po.Books import Books
from src.friend.entity.vo.QueryTable import QueryTable
from src.friend.entity.vo.TableData import TableData


class BooksDB:
    def __init__(self,session: AsyncSession):
        self.session = session

    async def insert_data(self,data:Books):
        """插入书籍"""
        async with self.session.begin():
            self.session.add(data)

    async def get_data_list(self,data:QueryTable):
        """根据条件获取书籍的内容"""
        async with self.session.begin():
            statement = select(Books)
            count_statement = select(func.count()).select_from(Books)
            # 动态拼接查询条件
            if data.keywords:
                statement = statement.where(Books.tittle.like(f"%{data.keywords}%"))
                count_statement = count_statement.where(Books.tittle.like(f"%{data.keywords}%"))
            statement = statement.limit(data.pagesize).offset(data.page_num).order_by(Books.type_id)
            result = await self.session.exec(statement)
            total = await self.session.exec(count_statement)
            item = result.all()
            count = total.one()
            return TableData[Books](total=count,items=item)
    async def  update_data(self,data:Books):
        """更新书籍的信息"""
        async with self.session.begin():
            statement = update(Books).where(Books.id==data.id).values(tittle=data.tittle,type_id=data.type_id)
            await self.session.exec(statement)

# 工厂函数（业务内部调用用这个）
async def create_books_db() -> BooksDB:
    async with async_session() as session:
        return BooksDB(session)