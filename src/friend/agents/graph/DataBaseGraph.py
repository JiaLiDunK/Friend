from langgraph.graph import StateGraph
from loguru import logger


class DataBaseGraph():
    def __init__(self):
        self.runnable = None

    async def build_create_knowledge_graph(self):
        """异步构建一个根据书籍目录创建新的知识库"""
        logger.info("构建创建知识库的图")
        graph_build = StateGraph(DataBaseState)
        graph_build.add_node("should_create_knowledge_base",should_create_knowledge_base)
        graph_build.add_node("create_knowledge_base",create_knowledge_base)
        graph_build.add_edge(START,"should_create_knowledge_base")
        graph_build.add_conditional_edges(
            "should_create_knowledge_base",
            judge_knowledge_base,
            {
                "end":END,
                "continue":"create_knowledge_base"
            }
        )
        return graph_build.compile()
    async def run_create_knowledge_base(self):
        """运行图"""
        if self.runnable is None:
            self.runnable = await self.build_create_knowledge_graph()
        result = await self.runnable.ainvoke({
            "message":""
        })
        return result