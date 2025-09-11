import logging

from fastapi import APIRouter, Depends
from src.friend.entity.vo.QueryTable import QueryTable


knowledgeBaseRouter = APIRouter()

@knowledgeBaseRouter.post("/getList")
async def get_list(data:QueryTable,
                   ):
    logging.info(f"查询:{data}")

