from fastapi import Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from src.friend.config.DBConfig import get_session
from src.friend.entity.po.MessagePrompt import MessagePrompt


class PromptDB:
    def __init__(self,session: AsyncSession):
        self.session = session

    async def insert_data(self,data: MessagePrompt):
        """插入数据"""
        async with self.session.begin():
            self.session.add(data)
            return "添加成功"



#工厂函数
async def create_prompt_db(session: AsyncSession=Depends(get_session)) -> PromptDB:
    return PromptDB(session)