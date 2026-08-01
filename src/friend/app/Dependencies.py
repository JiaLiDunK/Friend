from fastapi import Request

from friend.config.LLMClient import LLMClient


def get_llm_client(request: Request) -> LLMClient:
    """依赖注入函数，获取LLMClient实例"""
    return request.app.state.llm_client