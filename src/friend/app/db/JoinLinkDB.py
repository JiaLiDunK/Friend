from typing import List

from sqlalchemy import func, update
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.friend.config.DBConfig import async_session
from src.friend.entity.po.JoinLink import JoinLink
from src.friend.entity.vo.QueryTable import QueryTable
from src.friend.entity.vo.TableData import TableData


class JoinLinkDB:
    def __init__(self,session: AsyncSession):
        self.session = session
    async def __aenter__(self):
        self.session = async_session()
        await self.session.__aenter__()
        return JoinLinkDB(self.session)
    async def __aexit__(self, exc_type, exc, tb):
        await self.session.__aexit__(exc_type, exc, tb)
    async def insert_data(self,data:JoinLink)->str:
        """添加单个数据"""
        self.session.add(data)
        await self.session.commit()
        return "添加成功"
    async def del_data(self,data:JoinLink):
        """删除单个数据"""
        await self.session.delete(data)
        await self.session.commit()
        return "删除成功"
    async def get_data_list(self,data:QueryTable):
        """获取数据"""
        statement = select(JoinLink)
        count_statement = select(func.count()).select_from(JoinLink)
        statement = statement.order_by(JoinLink.id).limit(data.pagesize).offset(data.page_num)
        if data.key_num:
            statement = statement.where(JoinLink.master_id == data.key_num)
            count_statement = count_statement.where(JoinLink.master_id == data.key_num)
        result = await self.session.exec(statement)
        total = await self.session.exec(count_statement)
        item = result.all()
        count = total.one()
        join_link_list = [JoinLink.model_validate(join_link) for join_link in item]
        return TableData[JoinLink](total=count, items=join_link_list).model_dump()
    async def insert_list(self,data:List[JoinLink])->str:
        """添加多个数据"""
        self.session.add_all(data)
        await self.session.commit()
        return "添加成功"
    async def get_data_by_id(self,data_id:int)->JoinLink:
        """根据id获取数据"""
        statement = select(JoinLink).where(JoinLink.id == data_id)
        result = await self.session.exec(statement)
        item = result.one()
        return JoinLink.model_validate(item)
    async def update_data_one(self,join_link_id:int,order_id:int):
        """增加order_id"""
        statement = update(JoinLink).where(JoinLink.id==join_link_id).values(order_id=order_id)
        await self.session.exec(statement)
        await self.session.commit()

# 工厂函数
async def create_join_link_db():
    async with async_session() as session:
        yield JoinLinkDB(session)
async def create_join_link_load():
    async with async_session() as session:
        return JoinLinkDB(session)