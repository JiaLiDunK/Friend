from langchain_core.messages import BaseMessage
from langchain_ollama import ChatOllama




class LLMClient:
    def __init__(self):
        self.ollama_llm = ChatOllama(
            model="huihui_ai/qwen3-abliterated:8b",
            reasoning=True,
            temperature=0.2,
        )




    async def use_ollama_llm(self, prompt: list[BaseMessage]):
        result = await self.ollama_llm.ainvoke(prompt)
        return result


