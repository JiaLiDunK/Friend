from fastapi import APIRouter, Depends
from loguru import logger

from src.friend.app.db.TypeDB import create_type_db, TypeDB
from src.friend.entity.R import R
from src.friend.entity.po.SysType import SysType
from src.friend.entity.vo.QueryTable import QueryTable

typeRouter = APIRouter()

@typeRouter.post("/getTypeList")
async def get_type_list(data: QueryTable,
                        type_db: TypeDB = Depends(create_type_db)):
    logger.info(f"查询的参数{data}")
    data = await type_db.get_type_list(data)
    return R.ok().messages("查询成功").data_dict(data)

@typeRouter.post("/insertType")
async def insert_type(data: SysType,
                      type_db: TypeDB = Depends(create_type_db)):
    logger.info(f"插入的参数{data}")
    result = await type_db.insert_type(data)
    return R.ok().messages(result)

@typeRouter.post("/updateType")
async def update_type(data: SysType,
                      type_db: TypeDB = Depends(create_type_db)):
    logger.info(f"修改的参数{data}")
    await type_db.update_type(data)
    return R.ok().messages("修改成功")
