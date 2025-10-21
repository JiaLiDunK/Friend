

from langchain_community.chat_models import ChatTongyi
from src.friend.app.db.MemoryDB import create_memory_db, MemoryDB
from src.friend.config.SettingConfig import settings


# 这个是关于长期记忆的节点
class MemoryNode:
    def __init__(self,memory_db:MemoryDB):
        self.memory_db = memory_db
        self.llm = ChatTongyi(
            model=settings.MODEL,
            api_key=settings.API_KEY_ALI,
            model_kwargs={
                "temperature": 0.0  # 让回答统一
            }
        )
    @classmethod
    async def create(cls):
        memory_db = await create_memory_db()
        return cls(memory_db)
    async def get_memory_long_mid(self,user_id:int):
        """获取中短期记忆"""
        long_data = await self.memory_db.get_long_term_one_data(user_id)
        text = "下述是长期记忆:\n"
        text += long_data.content
        mid_list = await self.memory_db.get_mid_term_three_data(user_id)
        text += "\n下述是中短期记忆:\n"
        for mid_data in mid_list:
            text += mid_data.content
        return text


async def get_memory_node()-> MemoryNode:
    if not hasattr(get_memory_node,"instance"):
        get_memory_node.instance = await MemoryNode.create()
    return get_memory_node.instance