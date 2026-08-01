from typing import List, Tuple

from langchain_core.tools import StructuredTool
from loguru import logger

from friend.app.db.QApairsDB import QApairsDB
from friend.config.DBConfig import async_session


class DataScoreTools:
    def __init__(self):
        pass



    async def create_score_qa(self,
                              data: List[Tuple[int, int]])->str:
        """给qa_pairs打分,数据格式是[(id,score),...]"""
        async with async_session() as session:
            for id_,score in data:
                logger.info(f"给数据集打分")
                qa_pairs_db = QApairsDB(session)
                await qa_pairs_db.update_score(id_,score)
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