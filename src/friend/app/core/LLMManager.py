import asyncio
import functools
import time
from datetime import datetime

from loguru import logger

from src.friend.app.core.AgentTokenHandler import TongyiTokenHandler, _current_handler
from src.friend.app.db.LlmCallLogsDB import LlmCallLogsDB, create_llm_call_logs_by_load
from src.friend.entity.po.LlmCallLogs import LlmCallLogs


class LLMManager:
    def __init__(self,llm_call_logs:LlmCallLogsDB):
        self.llm_call_logs = llm_call_logs
    @classmethod
    async def create(cls):
        llm_call_logs = await create_llm_call_logs_by_load()
        return cls(llm_call_logs)
    def tongyi_chat_token_time_logger(self,func):
        """这个是记录百炼进行chat的token和耗时"""
        @functools.wraps(func)
        async def wrapper(*args,**kwargs):
            log = LlmCallLogs()
            log.create_time = datetime.now()
            log.function_name = func.__name__
            start_time = time.perf_counter()
            try:
                result = await func(*args,**kwargs)
                logger.info("================\n"+result+"\n=========")
                end_time = time.perf_counter()
                log.elapsed_times = end_time - start_time
                ai_message = getattr(result.message,"response_metadata",{})
                token_usage = ai_message.get("token_usage")
                log.model_name = ai_message.get("model_name")
                log.input_tokens = token_usage.get("input_tokens",0)
                log.output_tokens = token_usage.get("output_tokens",0)
                log.total_tokens = token_usage.get("total_tokens",0)
                log.call_type = 12
                log.status = 14
                log.count = 1
                await self.llm_call_logs.insert_data(log)
                return result
            except Exception as e:
                log.elapsed_times = time.perf_counter() - start_time
                log.status = 15
                log.error_message = str(e)
                await self.llm_call_logs.insert_data(log)
                raise e
        return wrapper

    def ollama_chat_token_time_logger(self, func):
        """这个是记录ollama进行chat的token和耗时"""
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            log = LlmCallLogs()
            log.create_time = datetime.now()
            log.function_name = func.__name__
            start_time = time.perf_counter()
            try:
                result = await func(*args, **kwargs)
                end_time = time.perf_counter()
                log.elapsed_times = end_time - start_time
                gen = result.generations[0][0]
                info = gen.generation_info
                log.input_tokens = info.get("prompt_eval_count")
                log.model_name = info.get("model")
                log.output_tokens = info.get("eval_count")
                log.total_tokens = info.get("eval_count") + info.get("prompt_eval_count")
                log.call_type = 12
                log.status = 14
                log.count = 1
                await self.llm_call_logs.insert_data(log)
                return result
            except Exception as e:
                log.elapsed_times = time.perf_counter() - start_time
                log.status = 15
                log.error_message = str(e)
                await self.llm_call_logs.insert_data(log)
                raise e
        return wrapper
    def tongyi_agent_token_time_logger(self,func):
        """这个是记录百炼进行agent的token和耗时"""
        @functools.wraps(func)
        async def wrapper(*args,**kwargs):
            log = LlmCallLogs()
            log.create_time = datetime.now()
            log.function_name = func.__name__
            start_time = time.perf_counter()
            handler = TongyiTokenHandler()
            _current_handler.set(handler)  # 绑定当前上下文 handler
            try:
                result = await func(*args, **kwargs) # 执行异步的方法
                end_time = time.perf_counter()
                log.elapsed_times = end_time - start_time
                token_usage = await handler.get_usage()
                log.input_tokens = token_usage.get("input_tokens", 0)
                log.output_tokens = token_usage.get("output_tokens", 0)
                log.total_tokens = token_usage.get("total_tokens", 0)
                log.model_name = token_usage.get("model_name",0)
                log.call_type = 13
                log.status = 14
                log.count = token_usage.get("count",0)
                await self.llm_call_logs.insert_data(log)
                return result
            except Exception as e:
                logger.info(f"错误信息:{e}")
                log.elapsed_times = time.perf_counter() - start_time
                log.status = 15
                log.error_message = str(e)
                await self.llm_call_logs.insert_data(log)
                raise e
        return wrapper



_singleton_lock = asyncio.Lock()

async def get_llm_manager() -> LLMManager:
    if not hasattr(get_llm_manager, "instance"):
        async with _singleton_lock:
            if not hasattr(get_llm_manager, "instance"):
                get_llm_manager.instance = await LLMManager.create()
    return get_llm_manager.instance