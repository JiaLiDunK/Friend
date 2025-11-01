from langchain_community.chat_models import ChatTongyi

from src.friend.app.core.LLMManager import get_llm_manager, LLMManager
from src.friend.app.db.GirlfriendPromptDB import create_girlfriend_prompt_db, GirlfriendPromptDB
from src.friend.config.SettingConfig import settings


class GirlfriendNode:
    def __init__(self,girlfriend_prompt_db:GirlfriendPromptDB,llm_manager:LLMManager):
        self.llm = ChatTongyi(
            model=settings.MODEL,
            api_key=settings.API_KEY_ALI,  # 生成多样性控制
            model_kwargs={
                "temperature": 0.7  # 让回答统一
            }
        )
        self.girlfriend_prompt_db = girlfriend_prompt_db
    @classmethod
    async def create(cls):
        girlfriend_prompt_db = await create_girlfriend_prompt_db()
        llm_manager = await get_llm_manager()
        return cls(girlfriend_prompt_db,llm_manager)
    async def girl_chat(self):
        """开启简单的聊天"""
        data = await self.girlfriend_prompt_db.get_data_by_user_id(1)

async def get_chat_node() -> GirlfriendNode:
    if not hasattr(get_chat_node, "instance"):
        get_chat_node.instance = await GirlfriendNode.create()
    return get_chat_node.instance