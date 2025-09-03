from fastapi import APIRouter, Depends
from loguru import logger

from friend.app.db.TypeDB import create_type_db, TypeDB
from friend.entity.R import R
from friend.entity.po.SysType import SysType
from friend.entity.vo.QueryTable import QueryTable

typeRouter = APIRouter()

@typeRouter.post("/getTypeList")
async def get_type_list(data: QueryTable):
    logger.info(f"查询的参数{data}")
    pass

@typeRouter.post("/insertType")
async def insert_type(data: SysType,
                      type_db: TypeDB = Depends(create_type_db)):
    logger.info(f"插入的参数{data}")
    result = await type_db.insert_type(data)
    return R.ok().messages(result)