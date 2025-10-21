from fastapi import APIRouter, Depends
from loguru import logger

from src.friend.agents.graph.DataBaseGraph import DataBaseGraph, get_data_base_graph
from src.friend.agents.node.MilvusNode import MilvusNode, create_milvus_node
from src.friend.entity.ai.AIResponseMessage import AIResponseMessage

agentRouter = APIRouter()



@agentRouter.get("/test")
async def one_test_one(data_one:MilvusNode = Depends(create_milvus_node)):
    data = AIResponseMessage(
        knowledge_base_id=64,message="?")
    logger.info(f"进入了")
    data_list = await data_one.search_data_get_list(data)
    for data in data_list:
        logger.info(f"data={data}")
    return {"message": "Hello, World!::"}

@agentRouter.get("/knowledge_base")
async def knowledge_base(data_one:DataBaseGraph = Depends(get_data_base_graph)):
    await data_one.run_base("knowledge_base")
    return "ok"

@agentRouter.get("/book_vectors")
async def book_vectors(data_one:DataBaseGraph = Depends(get_data_base_graph)):
    await data_one.run_base("book_vectors")
    return "ok"