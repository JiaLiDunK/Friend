from typing import List

from fastapi import APIRouter, Depends

from src.friend.app.db.ChunkDB import ChunkDB, create_chunk_db
from src.friend.entity.R import R
from src.friend.app.db.JoinLinkDB import JoinLinkDB, create_join_link_db
from src.friend.entity.po.JoinLink import JoinLink
from src.friend.entity.vo.QueryTable import QueryTable
from loguru import logger

from src.friend.entity.vo.TypeOptions import SelectOptions

joinLinkRouter = APIRouter()

@joinLinkRouter.post("/getList")
async def get_list(data:QueryTable,join_link_db:JoinLinkDB=Depends(create_join_link_db)):
    logger.info(f"查询数据:{data}")
    result = await join_link_db.get_data_list(data)
    return R.ok().data_dict(result)
@joinLinkRouter.post("/addList")
async def add_list(data:List[SelectOptions],join_link_db:JoinLinkDB=Depends(create_join_link_db),chunk_db:ChunkDB=Depends(create_chunk_db)):
    logger.info(f"添加数据:{data}")
    insert_data:List[JoinLink] = []
    for item in data:
        sum_num = await chunk_db.get_count_by_id(item.uuid)
        insert_data.append(JoinLink(master_id=item.master_id,slave_id=item.slave_id,order_id=0,sun_num=sum_num))
    result = await join_link_db.insert_list(insert_data)
    return R.ok().messages(result)