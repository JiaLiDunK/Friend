from src.friend.app.db.LlmCallLogs import LlmCallLogs, create_llm_call_logs


class LLMManager:
    def __init__(self,llm_call_logs:LlmCallLogs):
        self.llm_call_logs = llm_call_logs
    @classmethod
    async def create(cls):
        llm_call_logs = await create_llm_call_logs()
        return cls(llm_call_logs)

async def get_llm_manager()->LLMManager:
    if not hasattr(get_llm_manager,"instance"):
        get_llm_manager.instance = await LLMManager.create()
    return get_llm_manager.instance