from src.friend.entity.po.LlmCallLogs import LlmCallLogs
from sqlmodel.ext.asyncio.session import AsyncSession

from src.friend.config.DBConfig import async_session


class LlmCallLogsDB:
    def __init__(self,session:AsyncSession):
        self.session = session
    async def insert_data(self,data:LlmCallLogs):
        """插入书籍"""
        async with self.session.begin():
            self.session.add(data)
# 工厂函数
async def create_llm_call_logs()->LlmCallLogsDB:
    async with async_session() as session:
        return LlmCallLogsDB(session)