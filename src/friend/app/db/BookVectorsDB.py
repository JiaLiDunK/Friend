from typing import List

from sqlmodel import select, update, func, delete, desc
from sqlmodel.ext.asyncio.session import AsyncSession

from src.friend.config.DBConfig import async_session
from src.friend.entity.po.BookVectors import BookVectors
from src.friend.entity.po.Books import Books
from src.friend.entity.vo.BookToVectors import BookToVectors
from src.friend.entity.vo.QueryTable import QueryTable
from src.friend.entity.vo.TableData import TableData


class BookVectorsDB:
    def __init__(self,session: AsyncSession):
        self.session = session
    async def __aenter__(self):
        self.session = async_session()
        await self.session.__aenter__()
        return BookVectorsDB(self.session)

    async def __aexit__(self, exc_type, exc, tb):
        await self.session.__aexit__(exc_type, exc, tb)
    async def insert_data(self,data:BookVectors):
        """插入书籍记录"""
        async with self.session.begin():
            self.session.add(data)
    async def update_data(self,data:BookVectors):
        """更新书籍记录"""
        async with self.session.begin():
            statement = update(BookVectors).where(BookVectors.id==data.id).values(uuid=data.uuid,type_id=data.type_id,knowledge_base_id=data.knowledge_base_id)
            await self.session.exec(statement)
    async def update_data_only_id(self,data:Books):
        """就更新书籍所在的书籍"""
        async with self.session.begin():
            statement = update(BookVectors).where(BookVectors.id == data.id).values(knowledge_base_id=data.knowledge_base_id)
            await self.session.exec(statement)
    async def get_data_list(self,data:QueryTable):
        """根据条件查询数据"""
        statement = select(BookVectors, Books.tittle).select_from(BookVectors).join(Books,
                                                                                    BookVectors.uuid == Books.uuid,
                                                                                    isouter=True)
        count_statement = select(func.count()).select_from(BookVectors).join(Books, BookVectors.uuid == Books.uuid,
                                                                             isouter=True)
        # 动态拼接查询条件
        if data.keywords:
            statement = statement.where(Books.tittle.like(f"%{data.keywords}%"))
            count_statement = count_statement.where(Books.tittle.like(f"%{data.keywords}%"))
        statement = statement.limit(data.pagesize).offset(data.page_num).order_by(desc(BookVectors.id))
        result = await self.session.exec(statement)
        total = await self.session.exec(count_statement)
        item = result.all()
        count = total.one()
        items = [
            BookToVectors(
                id=bv.id,
                uuid=bv.uuid,
                type_id=bv.type_id,
                knowledge_base_id=bv.knowledge_base_id,
                tittle=tittle,
            )
            for bv, tittle in item
        ]
        return TableData[BookToVectors](total=count, items=items)
    async def del_data(self,data:BookVectors):
        """根据id删除数据"""
        async with self.session.begin():
            statement = delete(BookVectors).where(BookVectors.id==data.id)
            await self.session.exec(statement)
    async def get_data_to_ai(self)->List[Books]:
        """获取前一百本书的名称"""
        statement = select(BookVectors.id, Books.tittle).select_from(BookVectors).join(Books,
                                                                                       BookVectors.uuid == Books.uuid,
                                                                                       isouter=True)
        statement = statement.where(BookVectors.knowledge_base_id == 0).limit(10).order_by(BookVectors.id)
        result = await self.session.exec(statement)
        item: List[Books] = result.all()
        return item
    async def get_uuid_list(self):
        """获取所有的uuid"""
        statement = select(BookVectors.uuid, BookVectors.knowledge_base_id).where(BookVectors.type_id == 8,
                                                                                  BookVectors.knowledge_base_id != 0)
        result = await self.session.exec(statement)
        item = result.all()
        return item

# 工厂函数
async def create_book_vectors_db():
    async with async_session() as session:
        yield BookVectorsDB(session)
async def create_book_vectors_db_by_load():
    async with async_session() as session:
        return BookVectorsDB(session)