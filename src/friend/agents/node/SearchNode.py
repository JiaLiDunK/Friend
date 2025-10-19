import json
from typing import List

from langchain_community.chat_models import ChatTongyi
from langchain_ollama import OllamaLLM
from loguru import logger

from src.friend.agents.node.MilvusNode import create_milvus_node, MilvusNode
from src.friend.agents.state.DataBaseState import DataBaseState
from src.friend.app.core.LLMManager import get_llm_manager, LLMManager
from src.friend.app.db.KnowledgeBaseDB import KnowledgeBaseDB
from src.friend.app.db.KnowledgeBaseDB import create_knowledge_base_db
from src.friend.app.db.PromptDB import create_prompt_db, PromptDB
from src.friend.config.SettingConfig import settings
from src.friend.entity.ai.AIResponseMessage import QuestionId
from src.friend.entity.ai.MilvusResponse import SelectContent


class SearchNode:
    def __init__(self,milvus_node:MilvusNode,knowledge_base_db:KnowledgeBaseDB,prompt_db:PromptDB,llm_manager:LLMManager):
        self.llm = ChatTongyi(
            model=settings.MODEL,
            api_key=settings.API_KEY_ALI,  # 生成多样性控制
            model_kwargs={
                "temperature": 0.0  # 让回答统一
            }
        )
        self.ollama = OllamaLLM(
            model="huihui_ai/qwen3-abliterated:8b",
            reasoning = True #这个是关闭思考模型的回复
        )
        self.milvus_node = milvus_node
        self.knowledge_base_db = knowledge_base_db
        self.prompt_db = prompt_db
        self.llm_manager = llm_manager
        # 用llm_manager的装饰器包装需要记录的函数
        self.send_message_llm = self.llm_manager.tongyi_chat_token_time_logger(
            self.send_message_llm
        )
    @classmethod
    async def create(cls):
        milvus_node = await create_milvus_node()
        knowledge_base_db = await create_knowledge_base_db()
        prompt_db = await create_prompt_db()
        llm_manager = await get_llm_manager()
        return cls(milvus_node,knowledge_base_db,prompt_db,llm_manager)
    async def send_message_llm(self,question:str):
        """获取扩充的问题"""
        # 1.获取系统提示词以及知识库相关的信息
        system_prompt = await self.prompt_db.get_prompt_by_id(5)
        knowledge_base_list = await self.knowledge_base_db.get_data_to_ai()
        system_prompt += "\n【已有的知识库信息】:"
        for item in knowledge_base_list:
            system_prompt += f"\n{item}"
        system_prompt += "\n 原问题: "+question
        responses = await self.llm.ainvoke(system_prompt)
        data:DataBaseState = DataBaseState(message=responses)
        return data
    async def expand_and_retrieve(self,question:str):
        """这个方法是扩充问题然后查询知识库"""
        # 1.获取系统提示词以及知识库相关的信息
        responses = await self.send_message_llm(question)
        responses = responses.message
        data_json = json.loads(responses.content)
        data_list = [QuestionId(**item) for item in data_json]
        result_list = []
        back_list:List[SelectContent] = []
        # 2.去知识库中查询相关的数据
        for item in data_list:
            result = await self.milvus_node.search_data_get_list(search_data=item)
            result_list.append(result)
        for data in result_list:
            for item in data:
                back_list.append(item)
        back_list.sort()
        back_list = back_list[:5]
        logger.info(f"本次查询到了:{len(back_list)}")
        system_messages = "你是一个助手，回答用户的问题\n"
        system_messages += f"用户的问题:{question}\n"
        system_messages += "参考资料:\n"
        count = 1
        for item in back_list:
            system_messages += f"{count}.{item.content}\n"
            count += 1
        ai_message = await self.llm.ainvoke(system_messages)
        return ai_message.content


async def get_search_node()-> SearchNode:
    if not hasattr(get_search_node,"instance"):
        get_search_node.instance = await SearchNode.create()
    return get_search_node.instance
