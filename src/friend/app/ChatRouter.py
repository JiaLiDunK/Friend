from fastapi import APIRouter
from fastapi.params import Depends
from loguru import logger

from src.friend.agents.node.GirlfriendNode import GirlfriendNode, get_girl_friend_node
from src.friend.agents.node.SearchNode import SearchNode, get_search_node
from src.friend.entity.R import R

chatRouter = APIRouter()


@chatRouter.post("/chatTest")
async def chat_test(data:SearchNode=Depends(get_search_node)):
    logger.info("知识库检索")
    result = await data.expand_and_retrieve("")
    return result
@chatRouter.post("/girlfriend")
async def girlfriend(message:str
        ,girl_node:GirlfriendNode=Depends(get_girl_friend_node)):
    logger.info("进入聊天页面")
    result = await girl_node.girl_chat(message)
    return R.ok().data_dict(result)