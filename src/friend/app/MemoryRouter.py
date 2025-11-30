from typing import List

from fastapi import APIRouter, Depends
from loguru import logger

from src.friend.app.db.MemoryDB import MemoryDB, create_memory_db_by_load
from src.friend.entity.R import R
from src.friend.entity.vo.QueryTable import QueryTable

memoryRouter = APIRouter()

@memoryRouter.post("/getMemoryList")
async def get_memory_list(data: QueryTable,memory_db:MemoryDB=Depends(create_memory_db_by_load)):
    logger.info("获取记忆列表: {}",data)
    data = await memory_db.get_memory_list(data)
    return R.ok().messages("查询成功").data_dict(data)

@memoryRouter.post("/del")
async def del_memory(id_list:List[int],memory_db:MemoryDB=Depends(create_memory_db_by_load)):
    logger.info("删除记忆: {}",id_list)
    await memory_db.del_data(id_list)
    return R.ok().messages("删除成功")
@memoryRouter.post("/recover")
async def recover_memory(id_list:List[int],memory_db:MemoryDB=Depends(create_memory_db_by_load)):
    logger.info("恢复记忆: {}",id_list)
    await memory_db.recover_data(id_list)
    return R.ok().messages("恢复成功")
