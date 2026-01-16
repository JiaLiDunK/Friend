from typing import List, Tuple

from langchain_core.tools import StructuredTool
from loguru import logger

from src.friend.app.db.QApairsDB import create_qa_pairs_load


class DataScoreTools:
    def __init__(self,qa_pairs_db):
        self.qa_pairs_db = qa_pairs_db

    @classmethod
    async def create(cls):
        qa_pairs_db = await create_qa_pairs_load()
        return cls(qa_pairs_db)

    async def create_score_qa(self,
                              data: List[Tuple[int, int]])->str:
        """给qa_pairs打分,数据格式是[(id,score),...]"""
        for id_,score in data:
            logger.info(f"给数据集打分")
            await self.qa_pairs_db.update_score(id_,score)
        return "打分成功"

    def get_tools(self):
        """注册为 LangChain 工具"""
        return [
            StructuredTool.from_function(
                coroutine=self.create_score_qa,     # 异步函数
                name="create_score_qa",
                description="给 qa_pairs 表中的数据打分"
            ),
        ]