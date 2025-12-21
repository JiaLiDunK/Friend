import uuid
from datetime import datetime

from fastapi import APIRouter, Depends
from loguru import logger

from src.friend.app.db.DatasetDB import DatasetDB, create_dataset_db
from src.friend.entity.R import R
from src.friend.entity.po.dataset import Dataset
from src.friend.entity.vo.QueryTable import QueryTable

datasetRouter = APIRouter()

@datasetRouter.post("/getList")
async def get_list(data:QueryTable,dataset_db:DatasetDB=Depends(create_dataset_db)):
    logger.info(f"查询数据:{data}")
    result = await dataset_db.get_data_list(data)
    return R.ok().data_dict(result)
@datasetRouter.post("/add")
async def add(data:Dataset,dataset_db:DatasetDB=Depends(create_dataset_db)):
    logger.info(f"添加数据:{data}")
    data.sole_uuid = str(uuid.uuid4())
    data.create_time = datetime.now()
    result = await dataset_db.insert_data(data)
    return R.ok().messages(result)
@datasetRouter.post("/delData")
async def del_data(data:Dataset,dataset_db:DatasetDB=Depends(create_dataset_db)):
    logger.info(f"删除数据:{data}")
    result = await dataset_db.del_data(data)
    return R.ok().messages(result)
@datasetRouter.post("/update")
async def update(data:Dataset,dataset_db:DatasetDB=Depends(create_dataset_db)):
    logger.info(f"更新数据:{data}")
    result = await dataset_db.update_data(data)
    return R.ok().messages(result)
@datasetRouter.post("/getOptions")
async def get_options(dataset_db:DatasetDB=Depends(create_dataset_db)):
    logger.info("获取选项")
    result = await dataset_db.get_options()
    return R.ok().data_dict(result)
