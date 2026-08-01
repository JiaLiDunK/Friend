import json
from typing import List

from fastapi import APIRouter, Depends
from loguru import logger

from src.friend.agents.node.DataBaseNode import DataBaseNode, get_data_base_node
from src.friend.app.db.BooksDB import BooksDB, create_books_db
from src.friend.app.db.JoinLinkDB import JoinLinkDB, create_join_link_db
from src.friend.app.db.QApairsDB import QApairsDB, create_qa_pairs_db, QApairs
from src.friend.entity.R import R
from src.friend.entity.vo.DataSetVo import DataSetVo
from src.friend.entity.vo.QueryTable import DownLoadJsonData, QAQueryTable

qa_pairsRouter = APIRouter()

@qa_pairsRouter.post("/getList")
async def get_list(data:QAQueryTable,qa_pairs_db:QApairsDB=Depends(create_qa_pairs_db)):
    logger.info(f"查询qa列表的数据:{data}")
    result = await qa_pairs_db.get_data_list(data)
    return R.ok().data_dict(result)

@qa_pairsRouter.post("/add")
async def add(data:QApairs,qa_pairs_db:QApairsDB=Depends(create_qa_pairs_db)):
    logger.info(f"添加数据:{data}")
    await qa_pairs_db.insert_data(data)
    return R.ok().messages("添加成功")
@qa_pairsRouter.post("/delData")
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
async def down_load_json(data:List[int],qa_pairs_db:QApairsDB=Depends(create_qa_pairs_db),
                         books_db:BooksDB=Depends(create_books_db)):
    logger.info(f"下载原始的数据:{data}")
    books_uuid = await books_db.get_books_by_ids(data)
    # 转换成前端需要的格式
    qa_list = await qa_pairs_db.get_data_json(books_uuid)
    result = [{"question": qa.question, "answer": qa.answer} for qa in qa_list]
    # 转成 JSON 字符串
    json_str = json.dumps(result, ensure_ascii=False, indent=2)
    logger.info(f"本次下载大小:{len(json_str)}")
    return json_str

@qa_pairsRouter.post("/downLoadJsonByScore")
async def down_load_json_by_score(data:DownLoadJsonData,books_db:BooksDB=Depends(create_books_db)
                                  ,qa_pairs_db:QApairsDB=Depends(create_qa_pairs_db)):
    logger.info(f"根据分数下载数据:{data}")
    books_uuid = await books_db.get_books_by_ids(data.id_list)
    qa_list = await qa_pairs_db.get_data_json_by_score(data=books_uuid,score=data.score)
    result = [{"question": qa.question, "answer": qa.answer} for qa in qa_list]
    # # 转成 JSON 字符串
    json_str = json.dumps(result, ensure_ascii=False, indent=2)
    logger.info(f"本次下载大小:{len(json_str)}")
    return json_str

@qa_pairsRouter.post("/downLoadJsonByContext")
async def down_load_json_by_context(data:DownLoadJsonData,books_db:BooksDB=Depends(create_books_db)
                                    ,qa_pairs_db:QApairsDB=Depends(create_qa_pairs_db)):
    logger.info(f"下载带有上下文的数据:{data}")
    books_uuid = await books_db.get_books_by_ids(data.id_list)
    qa_list = await qa_pairs_db.get_data_json_context(data=books_uuid,score=data.score)
    result = [{"context":qa.context,"question": qa.question, "answer": qa.answer} for qa in qa_list]
    # 转成 JSON 字符串
    json_str = json.dumps(result, ensure_ascii=False, indent=2)
    logger.info(f"本次下载大小:{len(json_str)}")
    return json_str


@qa_pairsRouter.post("/vectorAllQA")
async def vector_qa(data:DataSetVo
                    ,join_link_db:JoinLinkDB=Depends(create_join_link_db)
                    ,books_db:BooksDB=Depends(create_books_db)
        ,data_base_node:DataBaseNode=Depends(get_data_base_node)):
    """向量化所有的书"""
    logger.info(f"向量化指定的qa:{data}")
    # 获取从数据
    data_list = await join_link_db.get_by_master_id(data.id)
    for item in data_list:
        book = await books_db.get_data_by_id(item.slave_id)
        await data_base_node.vector_qa(book.uuid,"names"+str(data.id))
        break
    return R.ok().messages("向量化成功")