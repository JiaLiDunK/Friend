from sqlmodel.ext.asyncio.session import AsyncSession

from src.friend.config.DBConfig import async_session
from src.friend.entity.po.LlmCallLogs import LlmCallLogs


class LlmCallLogsDB:
    def __init__(self,session:AsyncSession):
        self.session = session
    async def __aenter__(self):
        self.session = async_session()
        await self.session.__aenter__()
        return LlmCallLogsDB(self.session)

    async def __aexit__(self, exc_type, exc, tb):
        await self.session.__aexit__(exc_type, exc, tb)
    async def insert_data(self,data:LlmCallLogs):
        """插入书籍"""
        async with self.session.begin():
            self.session.add(data)
# 工厂函数
async def create_llm_call_logs():
    async with async_session() as session:
        yield LlmCallLogsDB(session)
async def create_llm_call_logs_by_load():
    async with async_session() as session:
        return LlmCallLogsDB(session)