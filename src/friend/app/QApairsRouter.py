import json

from fastapi import APIRouter, Depends
from loguru import logger

from src.friend.app.db.QApairsDB import QApairsDB, create_qa_pairs_db,QApairs
from src.friend.entity.vo.QueryTable import QueryTable, DownLoadJsonData
from src.friend.entity.R import R
qa_pairsRouter = APIRouter()

@qa_pairsRouter.post("/getList")
async def get_list(data:QueryTable,qa_pairs_db:QApairsDB=Depends(create_qa_pairs_db)):
    logger.info(f"查询数据:{data}")
    return ""

@qa_pairsRouter.post("/add")
async def add(data:QApairs,qa_pairs_db:QApairsDB=Depends(create_qa_pairs_db)):
    logger.info(f"添加数据:{data}")
    await qa_pairs_db.insert_data(data)
    return R.ok().messages("添加成功")
@qa_pairsRouter.post("/del")
async def del_data(data:QApairs,qa_pairs_db:QApairsDB=Depends(create_qa_pairs_db)):
    logger.info(f"删除数据:{data}")
    await qa_pairs_db.del_data(data)
    return R.ok().messages("添加成功")
@qa_pairsRouter.post("/update")
async def update(data:QApairs,qa_pairs_db:QApairsDB=Depends(create_qa_pairs_db)):
    logger.info(f"更新数据:{data}")
    await qa_pairs_db.update_data(data)
    return R.ok().messages("添加成功")

@qa_pairsRouter.post("/downLoadJson")
async def down_load_json(data:DownLoadJsonData,qa_pairs_db:QApairsDB=Depends(create_qa_pairs_db)):
    logger.info(f"下载原始的数据:{data}")
    # 转换成前端需要的格式
    qa_list = await qa_pairs_db.get_data_json(data)
    result = [{"question": qa.question, "answer": qa.answer} for qa in qa_list]
    # 转成 JSON 字符串
    json_str = json.dumps(result, ensure_ascii=False, indent=2)
    return R.ok().data_dict(json_str)

@qa_pairsRouter.post("/DownLoadJsonByScore")
async def down_load_json_by_score(data:DownLoadJsonData,qa_pairs_db:QApairsDB=Depends(create_qa_pairs_db)):
    logger.info(f"根据分数下载数据:{data}")
    qa_list = await qa_pairs_db.get_data_json(data)
    result = [{"question": qa.question, "answer": qa.answer} for qa in qa_list]
    # 转成 JSON 字符串
    json_str = json.dumps(result, ensure_ascii=False, indent=2)
    return R.ok().data_dict(json_str)

@qa_pairsRouter.post("/DownLoadJsonByContext")
async def down_load_json_by_context(data:DownLoadJsonData,qa_pairs_db:QApairsDB=Depends(create_qa_pairs_db)):
    logger.info(f"下载带有上下文的数据:{data}")
    qa_list = await qa_pairs_db.get_data_json_context(data)
    result = [{"question": qa.question, "answer": qa.answer} for qa in qa_list]
    # 转成 JSON 字符串
    json_str = json.dumps(result, ensure_ascii=False, indent=2)
    return R.ok().data_dict(json_str)