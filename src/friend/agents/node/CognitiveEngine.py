# 认知引擎，处理理解、推理、总结等
from typing import List
from loguru import logger
from langchain_community.chat_models import ChatTongyi
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage

from src.friend.agents.node.SearchNode import get_search_node, SearchNode
from src.friend.app.AgentRouter import knowledge_base
from src.friend.app.db.KnowledgeBaseDB import create_knowledge_base_db_by_load, KnowledgeBaseDB
from src.friend.app.db.PromptDB import create_prompt_db_by_load,PromptDB
from src.friend.config.SettingConfig import settings
from src.friend.entity.po.MessagePrompt import MessagePrompt


class CognitiveEngine:
    def __init__(self,prompt_db:PromptDB,knowledge_base_db:KnowledgeBaseDB,search_node:SearchNode):
        self.llm = ChatTongyi(
            model=settings.MODEL,
            api_key=settings.API_KEY_ALI,  # 生成多样性控制
            model_kwargs={
                "temperature": 0.1
            }
        )
        self.prompt_db = prompt_db
        self.search_node = search_node
        self.knowledge_base_db = knowledge_base_db
    @classmethod
    async def create(cls):
        prompt_db = await create_prompt_db_by_load()
        knowledge_base_db = await create_knowledge_base_db_by_load()
        search_node = await get_search_node()
        return cls(prompt_db,knowledge_base_db,search_node)
    async def entrance(self,prompt:str)->str:
        """这个是入口"""
        intent = await self.intent_recognition(prompt)
        data = await self.search_node.expand_and_retrieve(intent)
        message = "下面是关于情感和心理的参考资料:\n"
        i = 1
        for item in data:
            message += f"\n{i}."+item.content
        return message

    async def intent_recognition(self,prompt:str):
        # 用户的意图识别
        data = await self.prompt_db.get_prompt_by_id(6)
        prompt_list:List[BaseMessage] = [SystemMessage(data), HumanMessage(prompt)]
        result = await self.llm.ainvoke(prompt_list)
        logger.info(f"意图识别时的原聊天记录:{prompt}\n,返回的结果:{result.content}")
        return result.content

async def get_cognitive_engine_node() -> CognitiveEngine:
    if not hasattr(get_cognitive_engine_node,"instance"):
        get_cognitive_engine_node.instance = await CognitiveEngine.create()
    return get_cognitive_engine_node.instance