from typing import List

from sqlalchemy import func, update
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from src.friend.config.DBConfig import async_session
from src.friend.entity.po.KnowledgeBase import KnowledgeBase
from src.friend.entity.vo.QueryTable import QueryTable
from src.friend.entity.vo.TableData import TableData
from src.friend.entity.vo.TypeOptions import TypeOptions


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
            statement = update(KnowledgeBase).where(KnowledgeBase.id==data.id).values(collection_remark=data.collection_remark,data_base_remark=data.data_base_remark,collection=data.collection,data_base=data.data_base,type_id=data.type_id)
            await self.session.exec(statement)

    async def get_list(self,data:QueryTable):
        """根据参数查询数据库"""
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
        return TableData[KnowledgeBase](total=count, items=item)
    async def get_type_options(self):
        """获取类型选项"""
        statement = select(KnowledgeBase)
        result = await self.session.exec(statement)
        item = result.all()
        option_list: List[TypeOptions] = [
            TypeOptions(
                value=record.id,
                label=f"{record.data_base_remark}{record.collection_remark}"
            )
            for record in item
        ]
        return option_list
    async def get_data_to_ai(self)->List[KnowledgeBase]:
        """获取所有的数据"""
        statement = select(KnowledgeBase)
        result = await self.session.exec(statement)
        item: List[KnowledgeBase] = result.all()
        return item
    async def get_data_by_id(self,knowledge_id)->KnowledgeBase:
        """根据id获取数据"""
        statement = select(KnowledgeBase).where(KnowledgeBase.id == knowledge_id)
        result = await self.session.exec(statement)
        item = result.one()
        return item
    async def get_data_by_id_list(self,id_list:List[int])->List[KnowledgeBase]:
        """根据id列表获取配置信息"""
        statement = select(KnowledgeBase).where(KnowledgeBase.id.in_(id_list))
        result = await self.session.exec(statement)
        item = result.all()
        return item


# 工厂函数(内部业务调用这个)
async def create_knowledge_base_db():
    async with  async_session() as session:
        yield KnowledgeBaseDB(session)