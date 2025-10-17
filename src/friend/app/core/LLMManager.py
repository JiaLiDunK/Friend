import time
from functools import wraps
from datetime import datetime
from src.friend.entity.po.LlmCallLogs import LlmCallLogs
from src.friend.app.db.LlmCallLogsDB import LlmCallLogsDB, create_llm_call_logs

# 注意:暂时用不到
class LLMManager:
    def __init__(self,llm_call_logs:LlmCallLogsDB):
        self.llm_call_logs = llm_call_logs
    @classmethod
    async def create(cls):
        llm_call_logs = await create_llm_call_logs()
        return cls(llm_call_logs)
    async def tongyi_chat_token_time_logger(self,func):
        """这个是记录百炼的token和耗时"""
        @wraps(func)
        def wrapper(*args,**kwargs):
            log = LlmCallLogs()
            log.function_name = func.__name__
            start_time = time.perf_counter()
            try:
                result = func(*args,**kwargs)
                end_time = time.perf_counter()
                log.elapsed_time = end_time - start_time
                token_usage = getattr(result,"response_metadata",{}).get("token_usage",{})
                log.model_name = getattr(result, "response_metadata", {}).get("model_name", {})
                log.input_tokens = token_usage.get("input_tokens",0)
                log.output_tokens = token_usage.get("output_tokens",0)
                log.total_tokens = token_usage.get("total_tokens",0)
                log.create_time = datetime.now()
                log.call_type = 12
                log.status = 14
                self.llm_call_logs.insert_data(log)
                return result
            except Exception as e:
                log.elapsed_time = time.perf_counter() - start_time
                log.status = 15
                log.error_message = str(e)
                self.llm_call_logs.insert_data(log)
                raise e
        return wrapper

async def get_llm_manager()->LLMManager:
    if not hasattr(get_llm_manager,"instance"):
        get_llm_manager.instance = await LLMManager.create()
    return get_llm_manager.instance