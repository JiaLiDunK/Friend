from sqlmodel.ext.asyncio.session import AsyncSession

from src.friend.config.DBConfig import async_session


class AgentsDB:
    def __init__(self,session: AsyncSession):
        self.session = session


# 工厂函数
async def create_agents_db() -> AgentsDB:
    async with async_session() as session:
        return AgentsDB(session)