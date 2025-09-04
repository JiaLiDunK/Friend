from fastapi import Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from src.friend.config.DBConfig import get_session


class AgentsDB:
    def __init__(self,session: AsyncSession):
        self.session = session


# 工厂函数
async def create_agents_db(session: AsyncSession=Depends(get_session)) -> AgentsDB:
    return AgentsDB(session)