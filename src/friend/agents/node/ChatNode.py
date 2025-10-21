from langchain_community.chat_models import ChatTongyi

from src.friend.agents.node.SearchNode import get_search_node, SearchNode
from src.friend.app.core.LLMManager import get_llm_manager, LLMManager
from src.friend.app.db.PromptDB import PromptDB, create_prompt_db
from src.friend.config.SettingConfig import settings


class ChatNode:
    def __init__(self,search_node:SearchNode,llm_manager:LLMManager,prompt_db:PromptDB):
        self.llm = ChatTongyi(
            model=settings.MODEL,
            api_key=settings.API_KEY_ALI,  # 生成多样性控制
            model_kwargs={
                "temperature": 0.7  # 让回答统一
            }
        )
        self.search_node = search_node
        self.llm_manager = llm_manager
        self.prompt_db = prompt_db

    @classmethod
    async def create(cls):
        search_node = await get_search_node()
        llm_manager = await get_llm_manager()
        prompt_db = await create_prompt_db()
        return cls(search_node,llm_manager,prompt_db)

    async def chat(self,data):
        """聊天的模型"""
        system_prompt = await self.prompt_db.get_prompt_by_id(7)
        result = await self.llm.ainvoke(system_prompt + "\n" + data)
        #启动后台任务（不会阻塞）
        # asyncio.create_task(self.process_book(data, result))
        return result

async def get_chat_node()-> ChatNode:
    if not hasattr(get_chat_node,"instance"):
        get_chat_node.instance = await ChatNode.create()
    return get_chat_node.instance