from typing import List

from sqlmodel import select, update, func
from sqlmodel.ext.asyncio.session import AsyncSession

from src.friend.config.DBConfig import async_session
from src.friend.entity.po.Books import Books
from src.friend.entity.po.JoinLink import JoinLink
from src.friend.entity.vo.QueryTable import QueryTable
from src.friend.entity.vo.TableData import TableData


class BooksDB:
    def __init__(self,session: AsyncSession):
        self.session = session
    async def __aenter__(self):
        self.session = async_session()
        await self.session.__aenter__()
        return BooksDB(self.session)

    async def __aexit__(self, exc_type, exc, tb):
        await self.session.__aexit__(exc_type, exc, tb)

    async def insert_data(self,data:Books):
        """插入书籍"""
        async with self.session.begin():
            self.session.add(data)

    async def get_data_list(self,data:QueryTable):
        """根据条件获取书籍的内容"""
        statement = select(Books)
        count_statement = select(func.count()).select_from(Books)
        # 动态拼接查询条件
        if data.keywords:
            statement = statement.where(Books.tittle.like(f"%{data.keywords}%"))
            count_statement = count_statement.where(Books.tittle.like(f"%{data.keywords}%"))
        statement = statement.order_by(Books.type_id).limit(data.pagesize).offset(data.page_num)
        result = await self.session.exec(statement)
        total = await self.session.exec(count_statement)
        item = result.all()
        count = total.one()
        return TableData[Books](total=count,items=item).model_dump()
    async def  update_data(self,data:Books):
        """更新书籍的信息"""
        async with self.session.begin():
            statement = update(Books).where(Books.id==data.id).values(tittle=data.tittle,type_id=data.type_id)
            await self.session.exec(statement)
    async def get_data_by_id(self,data_id:int):
        """根据id获取书籍"""
        async with self.session.begin():
            statement = select(Books).where(Books.id==data_id)
            result = await self.session.exec(statement)
        return result.one()
    async def get_books_by_ids(self,data:List[int]):
        """获取数据集中的所有书籍的uuid"""
        statement = select(Books.uuid).join(JoinLink,Books.id==JoinLink.slave_id).where(JoinLink.master_id.in_(data))
        result = await self.session.exec(statement)
        return result.all()

# 工厂函数（业务内部调用用这个）
async def create_books_db():
    async with async_session() as session:
        yield BooksDB(session)
async def create_books_db_by_load():
    async with async_session() as session:
        return BooksDB(session)