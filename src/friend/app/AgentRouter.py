from fastapi import APIRouter, Depends

from src.friend.agents.node.DataBaseNode import DataBaseNode, get_data_base_node
from src.friend.agents.graph.DataBaseGraph import DataBaseGraph,get_data_base_graph

agentRouter = APIRouter()



@agentRouter.get("/test")
async def one_test_one(data_one:DataBaseGraph = Depends(get_data_base_graph)):
    # await data.should_create_book_vectors() knowledge_base
    await data_one.run_base("knowledge_base")
    # await data_one.run_base("book_vectors")
    return {"message": "Hello, World!::"}