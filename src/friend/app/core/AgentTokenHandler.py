import re

from langchain_core.callbacks import BaseCallbackHandler
from loguru import logger


class TongyiTokenHandler(BaseCallbackHandler):
    def __init__(self):
        self.total_tokens = 0
        self.count = 0
        self.input_tokens = 0
        self.output_tokens = 0
        self.model_name = ''

    def on_llm_start(self, serialized, prompts, **kwargs):
        """提取 model_name"""
        try:
            repr_str = serialized.get("repr", "")
            match = re.search(r"model_name='([^']+)'", repr_str)
            if match:
                self.model_name = match.group(1)
            else:
                self.model_name = "unknown"
            logger.info(f"[on_llm_start] 使用模型: {self.model_name}")
        except Exception as e:
            logger.info(f"解析模型名失败: {e}")
    async def on_llm_end(self, response, **kwargs):
        """LLM 调用结束时统计 token"""
        try:
            meta = response.generations[0][0].message.response_metadata
            usage = meta.get("token_usage",{})
            self.input_tokens += usage.get("input_tokens")
            self.output_tokens += usage.get("output_tokens")
            self.total_tokens += usage.get("total_tokens",0)
            self.count += 1
        except Exception as e:
            logger.info(f"错误信息{e}")
    async def print_usage(self):
        logger.info(
            f"累计调用 {self.count} 次, tokens={self.total_tokens}, 输入={self.input_tokens}, 输出={self.output_tokens},模型={self.model_name}")

    async def get_usage(self):
        """直接返回 token 使用统计"""
        return {
            "count": self.count,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "total_tokens": self.total_tokens,
            "model_name":self.model_name
        }

async def get_tongyi_token_handler()->TongyiTokenHandler:
    if not hasattr(get_tongyi_token_handler,"instance"):
        get_tongyi_token_handler.instance = TongyiTokenHandler()
    return get_tongyi_token_handler.instance