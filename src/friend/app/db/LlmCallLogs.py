from sqlmodel.ext.asyncio.session import AsyncSession

from src.friend.config.DBConfig import async_session


class LlmCallLogs:
    def __init__(self,session:AsyncSession):
        self.session = session

# 工厂函数
async def create_llm_call_logs()->LlmCallLogs:
    async with async_session() as session:
        return LlmCallLogs(session)