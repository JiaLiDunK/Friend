from sqlalchemy import delete, update
from src.friend.entity.po.BookKnowledgeId import BookKnowledgeId
from sqlmodel.ext.asyncio.session import AsyncSession

from src.friend.config.DBConfig import async_session

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
# 工厂函数
async def create_agents_db():
    async with async_session() as session:
        yield BookKnowledgeIdDB(session)
async def create_agents_db_by_load():
    async with async_session() as session:
        return BookKnowledgeIdDB(session)
