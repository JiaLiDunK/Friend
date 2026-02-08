from langchain_community.chat_models import ChatTongyi
from langchain_ollama import OllamaLLM

from src.friend.app.core.LLMManager import get_llm_manager, LLMManager
from src.friend.config.SettingConfig import settings


class ChatNode:
    def __init__(self,llm_manager:LLMManager):
        self.qwen_plus_zero_seven = ChatTongyi(
            model=settings.MODEL,
            api_key=settings.API_KEY_ALI,  # 生成多样性控制
            model_kwargs={
                "temperature": 0.7  # 让回答统一
            }
        )
        self.ollamaLLm_8_b = OllamaLLM(
            model="huihui_ai/qwen3-abliterated:8b",
            reasoning=True,
            temperature=0.2
        )
        self.llm_manager = llm_manager
        # 用llm_manager的装饰器包装需要记录的函数
        self.user_ollama_qwen3_abliterated_8b_7 = self.llm_manager.ollama_chat_token_time_logger(
            self.user_ollama_qwen3_abliterated_8b_7
        )

    @classmethod
    async def create(cls):
        llm_manager = await get_llm_manager()
        return cls(llm_manager)

    async def user_ollama_qwen3_abliterated_8b_7(self,prompt:str):
        """从文本块中获取json字符串"""
        result = await self.ollamaLLm_8_b.agenerate_prompt([self.ollamaLLm_8_b._convert_input(prompt)])
        # .generations[0][0].text
        return result



async def get_chat_node()-> ChatNode:
    if not hasattr(get_chat_node,"instance"):
        get_chat_node.instance = await ChatNode.create()
    return get_chat_node.instance