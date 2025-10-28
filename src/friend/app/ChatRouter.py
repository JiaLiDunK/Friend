from fastapi import APIRouter
from fastapi.params import Depends
from loguru import logger

from src.friend.agents.node.SearchNode import SearchNode, get_search_node

chatRouter = APIRouter()


@chatRouter.post("/chatTest")
async def chat_test(data:SearchNode=Depends(get_search_node)):
    logger.info("知识库检索")
    result = await data.expand_and_retrieve("")
    return result
@chatRouter.post("/girlfriend")
async def girlfriend():
    logger.info("进入聊天页面")
    return "ok了"