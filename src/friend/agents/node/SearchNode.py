import json
from typing import List

from langchain_community.chat_models import ChatTongyi

from src.friend.agents.node.MilvusNode import create_milvus_node, MilvusNode
from src.friend.app.db.KnowledgeBaseDB import KnowledgeBaseDB
from src.friend.app.db.KnowledgeBaseDB import create_knowledge_base_db
from src.friend.app.db.PromptDB import create_prompt_db, PromptDB
from src.friend.config.SettingConfig import settings
from src.friend.entity.ai.AIResponseMessage import AIResponseMessage


class SearchNode:
    def __init__(self,milvus_node:MilvusNode,knowledge_base_db:KnowledgeBaseDB,prompt_db:PromptDB):
        self.llm = ChatTongyi(
            model=settings.MODEL,
            api_key=settings.API_KEY_ALI,  # 生成多样性控制
            model_kwargs={
                "temperature": 0.0  # 让回答统一
            }
        )
        self.milvus_node = milvus_node
        self.knowledge_base_db = knowledge_base_db
        self.prompt_db = prompt_db
    @classmethod
    async def create(cls):
        milvus_node = await create_milvus_node()
        knowledge_base_db = await create_knowledge_base_db()
        prompt_db = await create_prompt_db()
        return cls(milvus_node,knowledge_base_db,prompt_db)
    async def expand_and_retrieve(self,question:str):
        """这个方法是扩充问题然后查询知识库"""
        # 1.获取系统提示词以及知识库相关的信息
        system_prompt = await self.prompt_db.get_prompt_by_id(5)
        knowledge_base_list = await self.knowledge_base_db.get_data_to_ai()
        system_prompt += "\n【已有的知识库信息】:"
        for item in knowledge_base_list:
            system_prompt += f"\n{item}"
        system_prompt += "\n 原问题: "+question
        responses = await self.llm.ainvoke(system_prompt)
        data_json = json.loads(responses.content)
        data_list = List[AIResponseMessage](**data_json)
        result_list = []
        # 2.去知识库中查询相关的数据
        # 先不执行了
        return
        for item in data_list:
            result = await self.milvus_node.search_data_get_list(item.content)
            result_list.append(result)


