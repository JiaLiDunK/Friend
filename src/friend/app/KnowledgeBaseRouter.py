import logging

from fastapi import APIRouter, Depends
from friend.app.db.KnowledgeBaseDB import KnowledgeBaseDB, create_knowledge_base_db
from src.friend.app.db.TypeDB import create_type_db, TypeDB
from src.friend.entity.R import R
from src.friend.entity.po.SysType import SysType
from src.friend.entity.vo.QueryTable import QueryTable


knowledgeBaseRouter = APIRouter()

@knowledgeBaseRouter.post("/getList")
async def get_list(data:QueryTable,
                   knowledge_base_db:KnowledgeBaseDB=Depends(create_knowledge_base_db)):
    logging.info(f"查询:{data}")

