from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.friend.config.DBConfig import async_session
from src.friend.entity.po.GirlfriendPrompt import GirlfriendPrompt


class GirlfriendPromptDB:
    def __init__(self,session: AsyncSession):
        self.session = session
    async def __aenter__(self):
        self.session = async_session()
        await self.session.__aenter__()
        return GirlfriendPromptDB(self.session)

    async def __aexit__(self, exc_type, exc, tb):
        await self.session.__aexit__(exc_type, exc, tb)
    async def get_data_by_user_id(self,user_id:int) -> GirlfriendPrompt:
        """根据id获取数据"""
        statement = select(GirlfriendPrompt).where(GirlfriendPrompt.type_id==2,GirlfriendPrompt.user_id==user_id)
        result =  await self.session.exec(statement)
        item:GirlfriendPrompt = result.one()
        return item
# 工厂函数
async def create_girlfriend_prompt_db():
    async with async_session() as session:
        yield GirlfriendPromptDB(session)
async def create_girlfriend_prompt_db_by_load():
    async with async_session() as session:
        return GirlfriendPromptDB(session)