from sqlmodel.ext.asyncio.session import AsyncSession

from src.friend.config.DBConfig import async_session

class QuestionDB:
    def __init__(self,session: AsyncSession):
        self.session = session
    async def __aenter__(self):
        self.session = async_session()
        await self.session.__aenter__()
        return QuestionDB(self.session)
    async def __aexit__(self, exc_type, exc, tb):
        await self.session.__aexit__(exc_type, exc, tb)

# 工厂函数
async def create_agents_db():
    async with async_session() as session:
        yield QuestionDB(session)
async def create_agents_db_by_load():
    async with async_session() as session:
        return QuestionDB(session)