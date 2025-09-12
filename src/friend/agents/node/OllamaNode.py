from langchain_ollama import OllamaLLM


class OllamaNode:
    def __init__(self,model_name: str):
        self.ollama_obliterated = OllamaLLM(
            model = model_name,
            reasoning = True # 关闭思考模型的回复
        )
        self.ollama = OllamaLLM(
            model=model_name,
        )

    async def unlimited_chat_ollama(self, system_message:str,user_message:str):
        """访问的是无限制的大模型"""
        prompt = [
            system_message,user_message
        ]
        return await self.ollama_obliterated.ainvoke(prompt)
    async def chat_ollama(self, system_message:str,user_message:str):
        """访问的是有限制的大模型"""
        prompt = [
            system_message, user_message
        ]
        return await self.ollama.ainvoke(prompt)