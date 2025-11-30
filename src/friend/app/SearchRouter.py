from fastapi import APIRouter, Depends
from loguru import logger

from src.friend.agents.node.SearchNode import SearchNode, get_search_node
from src.friend.entity.R import R
from src.friend.entity.vo.QueryTable import SearchData

searchRouter = APIRouter()

@searchRouter.post("/send")
async def send(data:SearchData,search_node:SearchNode=Depends(get_search_node)):
    logger.info("搜索: {}",data)
    message = await search_node.search_know_base(data)
    return R.ok().messages("搜索成功").data_dict(message)
