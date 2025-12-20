from fastapi import APIRouter, Depends
from src.friend.entity.R import R
from src.friend.app.db.JoinLinkDB import JoinLinkDB, create_join_link_db
from src.friend.entity.po.JoinLink import JoinLink
from src.friend.entity.vo.QueryTable import QueryTable
from loguru import logger
joinLinkRouter = APIRouter()

@joinLinkRouter.post("/getList")
async def get_list(data:QueryTable,join_link_db:JoinLinkDB=Depends(create_join_link_db)):
    logger.info(f"查询数据:{data}")
    result = await join_link_db.get_data_list(data)
    return R.ok().data_dict(result)
@joinLinkRouter.post("/add")
async def add(data:JoinLink,join_link_db:JoinLinkDB=Depends(create_join_link_db)):
    logger.info(f"添加数据:{data}")
    result = await  join_link_db.insert_data(data)
    return R.ok().messages(result)
@joinLinkRouter.post("/delData")
async def del_data(data:JoinLink,join_link_db:JoinLinkDB=Depends(create_join_link_db)):
    logger.info(f"删除数据:{data}")
    result = await join_link_db.del_data(data)
    return R.ok().messages(result)
