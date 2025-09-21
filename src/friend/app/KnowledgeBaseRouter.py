import logging

from fastapi import APIRouter, Depends

from src.friend.app.db.KnowledgeBaseDB import create_knowledge_base_db,KnowledgeBaseDB
from src.friend.entity.R import R
from src.friend.entity.po.KnowledgeBase import KnowledgeBase
from src.friend.entity.vo.QueryTable import QueryTable

knowledgeBaseRouter = APIRouter()

@knowledgeBaseRouter.post("/getList")
async def get_list(data:QueryTable,
                   knowledge_base_db:KnowledgeBaseDB=Depends(create_knowledge_base_db)):
    logging.info(f"查询:{data}")
    data = await knowledge_base_db.get_list(data)
    return R.ok().messages("查询成功").data_dict(data)

@knowledgeBaseRouter.post("/insert")
async def insert(data:KnowledgeBase,
                 knowledge_base_db:KnowledgeBaseDB=Depends(create_knowledge_base_db)):
    logging.info(f"插入:{data}")
    data.id = None
    await knowledge_base_db.insert_data(data)
    return R.ok().messages("插入成功")

@knowledgeBaseRouter.post("/update")
async def update(data:KnowledgeBase,
                 knowledge_base_db:KnowledgeBaseDB=Depends(create_knowledge_base_db)):
    logging.info(f"更新数据:{data}")
    await knowledge_base_db.update_data(data)
    return R.ok().messages("更新成功")


