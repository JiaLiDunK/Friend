from src.friend.entity.vo.TableData import TableData
from sqlalchemy import func
from sqlmodel import select
from src.friend.entity.vo.QueryTable import QueryTable
from sqlmodel.ext.asyncio.session import AsyncSession
from src.friend.entity.po.JoinLink import JoinLink
from src.friend.config.DBConfig import async_session


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
        result = await self.session.exec(statement)
        total = await self.session.exec(count_statement)
        item = result.all()
        count = total.one()
        join_link_list = [JoinLink.model_validate(join_link) for join_link in item]
        return TableData[JoinLink](total=count, items=join_link_list).model_dump()


# 工厂函数
async def create_join_link_db():
    async with async_session() as session:
        yield JoinLinkDB(session)
async def create_join_link_load():
    async with async_session() as session:
        return JoinLinkDB(session)