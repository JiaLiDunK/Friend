from typing import List

from langchain_community.chat_models import ChatTongyi
from langchain_core.messages import SystemMessage, HumanMessage, BaseMessage

from src.friend.agents.node.CognitiveEngine import get_cognitive_engine_node, CognitiveEngine
from src.friend.app.core.LLMManager import get_llm_manager, LLMManager
from src.friend.app.db.GirlfriendPromptDB import GirlfriendPromptDB, \
    create_girlfriend_prompt_db_by_load
from src.friend.app.db.MemoryDB import create_memory_db_by_load, MemoryDB
from src.friend.config.SettingConfig import settings


class GirlfriendNode:
    def __init__(self,girlfriend_prompt_db:GirlfriendPromptDB,llm_manager:LLMManager,memory_db:MemoryDB,cognitive_engine:CognitiveEngine):
        self.llm = ChatTongyi(
            model=settings.MODEL,
            api_key=settings.API_KEY_ALI,  # 生成多样性控制
            model_kwargs={
                "temperature": 0.7  # 让回答统一
            }
        )
        self.girlfriend_prompt_db = girlfriend_prompt_db
        self.memory_db = memory_db
        self.cognitive_engine = cognitive_engine
    @classmethod
    async def create(cls):
        girlfriend_prompt_db = await create_girlfriend_prompt_db_by_load()
        memory_db = await create_memory_db_by_load()
        llm_manager = await get_llm_manager()
        cognitive_engine = await get_cognitive_engine_node()
        return cls(girlfriend_prompt_db,llm_manager,memory_db,cognitive_engine)
    async def girl_chat(self,message:str):
        """开启简单的聊天"""
        # await self.memory_db.insert_data_user(message,1)
        data = await self.girlfriend_prompt_db.get_data_by_user_id(1)
        system = data.prompt
        ten_data = await self.memory_db.get_short_term_ten_data(1)
        user_messages:str = ''
        # 先不添加记忆
        for item in ten_data:
            # 添加短期的记忆,最近十次的聊天记录
            if item.type_id == 17: # 获取整个
                user_messages += item.content
                user_messages += "\n"
            #     prompt.append(HumanMessage(item.content))
            # elif item.type_id == 16: # 表示是ai方的
            #     prompt.append(AIMessage(item.content))
        qing = await self.cognitive_engine.entrance(user_messages)
        prompt: List[BaseMessage] = [
            SystemMessage(system+qing),
        ]
        # 最后再添加此次的聊天记录
        prompt.append(HumanMessage(message))
        print("输出一下提示词:")
        print(prompt)
        result = await self.llm.ainvoke(prompt)
        # await self.memory_db.insert_data_ai(result.content,1)
        return result.content

async def get_girl_friend_node() -> GirlfriendNode:
    if not hasattr(get_girl_friend_node, "instance"):
        get_girl_friend_node.instance = await GirlfriendNode.create()
    return get_girl_friend_node.instance