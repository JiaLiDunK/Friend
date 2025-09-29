from langgraph.constants import START, END
from langgraph.graph import StateGraph
from loguru import logger

from src.friend.agents.node.DataBaseNode import DataBaseNode
from src.friend.agents.state.DataBaseState import DataBaseState

class DataBaseGraph:
    def __init__(self, data_base_node: DataBaseNode):
        # 存储不同graph的runnable
        self.runnable_map = {}
        self.data_base_node = data_base_node
    @classmethod
    async def create(cls):
        data_base_node = await DataBaseNode.create()
        return cls(data_base_node)
    async def build_create_knowledge_graph(self):
        """异步构建一个根据书籍目录创建新的知识库"""
        graph_build = StateGraph(DataBaseState)
        graph_build.add_node("should_create_knowledge_base",self.data_base_node.should_create_knowledge_base)
        graph_build.add_node("create_data_base",self.data_base_node.create_data_base)
        graph_build.add_edge(START,"should_create_knowledge_base")
        graph_build.add_conditional_edges(
            "should_create_knowledge_base",
            self.data_base_node.judge_create,
            {
                "end":END,
                "continue":"create_data_base"
            }
        )
        return graph_build.compile()
    async def build_create_book_graph(self):
        """异步构建一个根据知识库分类书籍"""
        graph_build = StateGraph(DataBaseState)
        graph_build.add_node("should_create_book_vectors",self.data_base_node.should_create_book_vectors)
        graph_build.add_node("create_data_base",self.data_base_node.create_data_base)
        graph_build.add_edge(START,"should_create_book_vectors")
        graph_build.add_conditional_edges(
            "should_create_book_vectors",
            self.data_base_node.judge_create,
            {
                "end":END,
                "continue":"create_data_base"
            }
        )
        return graph_build.compile()

    async def get_runnable(self,graph_type:str):
        """根据类型获取或者构建graph"""
        if graph_type not in self.runnable_map:
            if graph_type == "knowledge_base":
                self.runnable_map[graph_type] = await self.build_create_knowledge_graph()
            elif graph_type == "book_vectors":
                self.runnable_map[graph_type] = await self.build_create_book_graph()
            else:
                raise ValueError(f"不支持的graph类型:{graph_type}")
        return self.runnable_map[graph_type]

    async def run_base(self,graph_type:str):
        """根据类型运行不一样的graph"""
        runnable = await self.get_runnable(graph_type)
        result = await runnable.ainvoke({"message":""})
        return result

async def get_data_base_graph()->DataBaseGraph:
    if not hasattr(get_data_base_graph,"instance"):
        get_data_base_graph.instance = await DataBaseGraph.create()
    return get_data_base_graph.instance