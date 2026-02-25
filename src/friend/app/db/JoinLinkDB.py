from typing import List

from sqlalchemy import func, update
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.friend.config.DBConfig import async_session
from src.friend.entity.po.Books import Books
from src.friend.entity.po.JoinLink import JoinLink
from src.friend.entity.po.dataset import Dataset
from src.friend.entity.vo.BookToVectors import JoinLinkBook
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
        statement = select(JoinLink,Books.tittle,Dataset.description).join(Books,JoinLink.slave_id==Books.id).join(Dataset,JoinLink.master_id==Dataset.id)
        count_statement = select(func.count()).select_from(JoinLink)
        statement = statement.order_by(JoinLink.id).limit(data.pagesize).offset(data.page_num)
        if data.key_num:
            statement = statement.where(JoinLink.master_id == data.key_num)
            count_statement = count_statement.where(JoinLink.master_id == data.key_num)
        result = await self.session.exec(statement)
        total = await self.session.exec(count_statement)
        rows = result.all()  # 每个是 Row: (JoinLink, tittle)
        items = []
        for join_link, tittle,description in rows:
            items.append(
                JoinLinkBook(
                    id=join_link.id,
                    master_id=join_link.master_id,
                    slave_id=join_link.slave_id,
                    order_id=join_link.order_id,
                    sun_num=join_link.sun_num,
                    scoring_completed=join_link.scoring_completed,
                    tittle=tittle,
                    description=description,
                )
            )
        count = total.one()
        return TableData[JoinLinkBook](total=count, items=items).model_dump()
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
    async def update_data_score(self,join_link_id:int,scoring_completed:int):
        """增加socre_id"""
        statement = update(JoinLink).where(JoinLink.id==join_link_id).values(scoring_completed=scoring_completed)
        await self.session.exec(statement)
        await self.session.commit()
    async def get_books_data_by_scoring(self,ids:int):
        """根据主id获取未提取的书籍id"""
        statement = select(JoinLink).where(JoinLink.master_id==ids,JoinLink.order_id <= JoinLink.sun_num).order_by(JoinLink.id)
        result = await self.session.exec(statement)
        return result.all()
    async def get_books_data_by_extract(self,ids:int):
        """根据主id获取未打分的书籍id"""
        statement = select(JoinLink).where(JoinLink.master_id==ids,JoinLink.scoring_completed <= JoinLink.sun_num).order_by(JoinLink.id)
        result = await self.session.exec(statement)
        return result.all()
    async def get_books_data_by_clear(self,ids:int):
        """根据数据集的id获取数据"""
        statement = select(JoinLink).where(JoinLink.master_id==ids,JoinLink.clear_id <= JoinLink.sun_num).order_by(JoinLink.id)
        result = await self.session.exec(statement)
        return result.all()
    async def update_clear_one(self,ids:int,clear_id:int):
        """clear_id的id加一"""
        statement = update(JoinLink).where(JoinLink.id==ids).values(clear_id=clear_id)
        await self.session.exec(statement)
        await self.session.commit()
# 工厂函数
async def create_join_link_db():
    async with async_session() as session:
        yield JoinLinkDB(session)
async def create_join_link_load():
    async with async_session() as session:
        return JoinLinkDB(session)