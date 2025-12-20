from fastapi import APIRouter, Depends
from src.friend.entity.R import R
from src.friend.app.db.QApairsDB import QApairsDB, create_qa_pairs_db
from src.friend.entity.vo.QueryTable import QueryTable
from loguru import logger
qa_pairsRouter = APIRouter()

@qa_pairsRouter.post("/getList")
async def get_list(data:QueryTable,qa_pairs_db:QApairsDB=Depends(create_qa_pairs_db)):
    logger.info(f"查询数据:{data}")
    return "getList"

@qa_pairsRouter.post("/add")
async def add(data:QueryTable,qa_pairs_db:QApairsDB=Depends(create_qa_pairs_db)):
    logger.info(f"添加数据:{data}")
    return "add"
@qa_pairsRouter.post("/del")
async def del_data(data:QueryTable,qa_pairs_db:QApairsDB=Depends(create_qa_pairs_db)):
    logger.info(f"删除数据:{data}")
    return "del"
@qa_pairsRouter.post("/update")
async def update(data:QueryTable,qa_pairs_db:QApairsDB=Depends(create_qa_pairs_db)):
    logger.info(f"更新数据:{data}")
    return "update"