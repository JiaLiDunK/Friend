from fastapi import Depends
from sqlalchemy import func, update
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from friend.entity.po.KnowledgeBase import KnowledgeBase
from friend.entity.vo.QueryTable import QueryTable
from friend.entity.vo.TableData import TableData
from src.friend.config.DBConfig import get_session


class KnowledgeBaseDB:
    def __init__(self,session: AsyncSession):
        self.session = session

    async def insert_data(self,data:KnowledgeBase):
        """插入数据"""
        async with self.session.begin():
            self.session.add(data)

    async def update_data(self,data:KnowledgeBase):
        """修改书籍"""
        async with self.session.begin():
            statement = update(KnowledgeBase).where(KnowledgeBase.id==data.id).values(collection_remark=data.collection_remark).values(data_base_remark=data.data_base_remark).values(collection=data.collection).values(data_base=data.data_base).values(data_base_type=data.data_base_type)
            await self.session.exec(statement)

    async def get_list(self,data:QueryTable):
        """根据参数查询数据库"""
        async with self.session.begin():
            statement = select(KnowledgeBase)
            count_statement = select(func.count()).select_from(KnowledgeBase)
            # 动态拼接查询条件
            if data.keywords:
                statement = statement.where(KnowledgeBase.collection_remark.like(f"%{data.keywords}%"))
                count_statement = count_statement.where(KnowledgeBase.collection_remark.like(f"%{data.keywords}%"))
            statement = statement.limit(data.pagesize).offset(data.page_num)
            result = await self.session.exec(statement)
            total = await self.session.exec(count_statement)
            item = result.all()
            count = total.one()
            return TableData[KnowledgeBase](total=count,items=item)



# 工厂函数
async def create_knowledge_base_db(session: AsyncSession=Depends(get_session)) -> KnowledgeBaseDB:
    return KnowledgeBaseDB(session)