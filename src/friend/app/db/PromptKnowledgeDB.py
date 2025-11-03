from sqlmodel.ext.asyncio.session import AsyncSession

from src.friend.config.DBConfig import async_session
class PromptKnowledgeDB:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def __aenter__(self):
        self.session = async_session()
        await self.session.__aenter__()
        return PromptKnowledgeDB(self.session)

    async def __aexit__(self, exc_type, exc, tb):
        await self.session.__aexit__(exc_type, exc, tb)



async def create_prompt_knowledge_db():
    async with async_session() as session:
        yield PromptKnowledgeDB(session)


async def create_prompt_knowledge_db_by_load():
    async with async_session() as session:
        return PromptKnowledgeDB(session)