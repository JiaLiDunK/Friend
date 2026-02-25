from typing import List

from sqlmodel import delete, update, select, func
from sqlmodel.ext.asyncio.session import AsyncSession

from src.friend.config.DBConfig import async_session
from src.friend.entity.po.BookKnowledgeId import BookKnowledgeId
from src.friend.entity.po.Books import Books
from src.friend.entity.po.KnowledgeBase import KnowledgeBase
from src.friend.entity.vo.BookToVectors import KnowledgeToBook
from src.friend.entity.vo.QueryTable import QueryTable
from src.friend.entity.vo.TableData import TableData


class BookKnowledgeIdDB:
    def __init__(self,session: AsyncSession):
        self.session = session
    async def __aenter__(self):
        self.session = async_session()
        await self.session.__aenter__()
        return BookKnowledgeIdDB(self.session)

    async def __aexit__(self, exc_type, exc, tb):
        await self.session.__aexit__(exc_type, exc, tb)
    async def insert_data(self,data:BookKnowledgeId):
        """插入数据"""
        async with self.session.begin():
            self.session.add(data)
    async def del_data(self,data_id:int):
        """删除数据"""
        async with self.session.begin():
            statement = delete(BookKnowledgeId).where(BookKnowledgeId.id==data_id)
            await self.session.exec(statement)
    async def update_type_id(self,data_id:int):
        """修改type的id"""
        async with self.session.begin():
            statement = update(BookKnowledgeId).where(BookKnowledgeId.id==data_id).values(type_id=-952722)
            await self.session.exec(statement)
    async def get_data_list(self,data:QueryTable):
        """获取数据"""
        statement = (select(BookKnowledgeId,Books.tittle,KnowledgeBase.data_base_remark,KnowledgeBase.collection_remark)
                     .select_from(BookKnowledgeId).join(Books,BookKnowledgeId.uuid==Books.uuid,isouter=True)
                     .join(KnowledgeBase,BookKnowledgeId.knowledge_base_id==KnowledgeBase.id,isouter=True))
        count_statement = select(func.count()).select_from(BookKnowledgeId)
        # 动态拼接查询条件
        if data.keywords:
            statement = statement.where(Books.tittle.like(f"%{data.keywords}"))
            count_statement = count_statement.where(Books.tittle.like(f"%{data.keywords}"))
        statement = statement.limit(data.pagesize).offset(data.page_num)
        result = await self.session.exec(statement)
        total = await self.session.exec(count_statement)
        item = result.all()
        count = total.one()
        items = [
            KnowledgeToBook(
                id=bk.id,
                uuid=bk.uuid,
                knowledge_base_id=bk.knowledge_base_id,
                type_id=bk.type_id,
                tittle=tittle,
                data_base_remark=data_base_remark_,
                collection_remark=collection_remark_
            )
            for bk, tittle, data_base_remark_, collection_remark_ in item
        ]
        return TableData[KnowledgeToBook](total=count,items=items)
    async def get_all_data(self) -> List[BookKnowledgeId]:
        """获取所有未向量的数据"""
        statement = select(BookKnowledgeId).where(BookKnowledgeId.type_id==9)
        result = await self.session.exec(statement)
        item: List[BookKnowledgeId] = result.all()
        return item
    async def update_all_type_list(self,data_list:List[BookKnowledgeId]):
        """更新数据"""
        ids = [item[0].id for item in data_list]
        if not ids:
            return
        statement = update(BookKnowledgeId).where(BookKnowledgeId.id.in_(ids)).values(type_id=11)
        await self.session.exec(statement)
        await self.session.commit()


# 工厂函数
async def create_book_vectors_knowledge_id_db():
    async with async_session() as session:
        yield BookKnowledgeIdDB(session)
async def create_book_vectors_knowledge_id_db_by_load():
    async with async_session() as session:
        return BookKnowledgeIdDB(session)
