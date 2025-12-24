from typing import List

from fastapi import APIRouter, Depends
from loguru import logger

from src.friend.agents.node.ReadNode import ReadNode, get_read_node
from src.friend.app.db.BooksDB import BooksDB, create_books_db_by_load
from src.friend.app.db.ChunkDB import ChunkDB, create_chunk_db
from src.friend.app.db.JoinLinkDB import JoinLinkDB, create_join_link_db
from src.friend.entity.R import R
from src.friend.entity.po.JoinLink import JoinLink
from src.friend.entity.vo.QueryTable import QueryTable
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

@joinLinkRouter.post("/createLoraData")
async def create_lora_data(data:JoinLink,books_db:BooksDB=Depends(create_books_db_by_load),read: ReadNode = Depends(get_read_node)):
    logger.info(f"创建lora数据:{data}")
    result = await books_db.get_data_by_id(data.slave_id)
    if result is None:
        logger.error(f"未找到 ID 为 {data.slave_id} 的书籍")
        return R.error().messages("未找到对应的书籍信息")
    if result.order_id >= result.sun_num:
        logger.error(f"ID 为 {data.slave_id} 的书籍已生成lora数据")
        return R.error().messages("书籍已生成lora数据")
    await read.start_create_lora_data(data.slave_id,result.uuid,data.sun_num)
    return R.ok().messages("创建lora数据成功")
@joinLinkRouter.post("/scoringLoraData")
async def scoring_lora_data(data:JoinLink,books_db:BooksDB=Depends(create_books_db_by_load),read: ReadNode = Depends(get_read_node)):
    logger.info(f"给数据集打分:{data}")
    result = await books_db.get_data_by_id(data.slave_id)
    if result is None:
        logger.error(f"未找到 ID 为 {data.slave_id} 的书籍")
        return R.error().messages("未找到对应的书籍信息")
    if result.scoring_completed is not None:
        logger.error(f"ID 为 {data.slave_id} 的书籍已打分完毕")
        return R.error().messages("数据集已打分完毕")

    return R.ok().messages("打分成功")