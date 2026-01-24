from langchain_community.chat_models import ChatTongyi
from langchain_ollama import OllamaLLM

from src.friend.config.SettingConfig import settings


class ChatNode:
    def __init__(self):
        self.qwen_plus_zero_seven = ChatTongyi(
            model=settings.MODEL,
            api_key=settings.API_KEY_ALI,  # 生成多样性控制
            model_kwargs={
                "temperature": 0.7  # 让回答统一
            }
        )
        self.ollamaLLm = OllamaLLM(
            model="huihui_ai/qwen3-abliterated:8b",
            reasoning=True,
            temperature=0.2
        )

    @classmethod
    async def create(cls):
        return cls()

    async def get_context_from_data(self,prompt:str)->str:
        """从文本块中获取json字符串"""
        result = await self.ollamaLLm.ainvoke(prompt)
        return result



async def get_chat_node()-> ChatNode:
    if not hasattr(get_chat_node,"instance"):
        get_chat_node.instance = await ChatNode.create()
    return get_chat_node.instance