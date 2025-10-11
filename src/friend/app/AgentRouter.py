from fastapi import APIRouter, Depends

from src.friend.agents.node.DataBaseNode import DataBaseNode, get_data_base_node
from src.friend.agents.graph.DataBaseGraph import DataBaseGraph,get_data_base_graph

agentRouter = APIRouter()



@agentRouter.get("/test")
async def one_test_one(data_one:DataBaseNode = Depends(get_data_base_node)):
    await data_one.data_to_chunk()
    return {"message": "Hello, World!::"}

@agentRouter.get("/knowledge_base")
async def knowledge_base(data_one:DataBaseGraph = Depends(get_data_base_graph)):
    await data_one.run_base("knowledge_base")
    return "ok"

@agentRouter.get("/book_vectors")
async def book_vectors(data_one:DataBaseGraph = Depends(get_data_base_graph)):
    await data_one.run_base("book_vectors")
    return "ok"