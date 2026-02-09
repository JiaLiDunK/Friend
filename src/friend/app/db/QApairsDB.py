from typing import List

from sqlalchemy import func, update
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.friend.config.DBConfig import async_session
from src.friend.entity.po.Books import Books
from src.friend.entity.po.Chunk import Chunk
from src.friend.entity.po.JoinLink import JoinLink
from src.friend.entity.po.QApairs import QApairs
from src.friend.entity.vo.QueryTable import QAQueryTable
from src.friend.entity.vo.TableData import TableData


class QApairsDB:
    def __init__(self,session: AsyncSession):
        self.session = session
    async def __aenter__(self):
        self.session = async_session()
        await self.session.__aenter__()
        return QApairsDB(self.session)

    async def __aexit__(self, exc_type, exc, tb):
        await self.session.__aexit__(exc_type, exc, tb)
    async def insert_data(self,data:QApairs):
        """添加单个数据"""
        self.session.add(data)
        await self.session.commit()
    async def del_data(self,data:QApairs):
        """删除单个数据"""
        await self.session.delete(data)
        await self.session.commit()
    async def insert_list(self,data_list:List[QApairs]):
        """批量插入数据"""
        self.session.add_all(data_list)
        await self.session.commit()
    async def update_data(self,data:QApairs):
        """更新数据"""
        await self.session.update(data)
        await self.session.commit()
    async def update_score(self,data_id:int,score:int):
        """更新数据"""
        statement = update(QApairs).where(QApairs.id==data_id).values(score=score)
        await self.session.exec(statement)
        await self.session.commit()
    async def get_data_by_uuid_order_id(self,uuid:str,chunk_id:int)->List[QApairs]:
        """根据uuid和orderid获取当前数据集"""
        statement = select(QApairs).where(QApairs.sole_uuid==uuid,QApairs.chunk_id==chunk_id)
        result = await self.session.exec(statement)
        data:List[QApairs] = result.all()
        return data
    async def get_data_json(self,data:List[str]):
        """获取json数据"""
        statement = select(QApairs).where(QApairs.sole_uuid.in_(data))
        result = await self.session.exec(statement)
        result_list:List[QApairs] = result.all()
        return result_list
    async def get_data_json_by_score(self,data:List[str],score:int):
        """获取json数据带有分数"""
        statement = select(QApairs).where(QApairs.sole_uuid.in_(data),QApairs.score>=score)
        result = await self.session.exec(statement)
        result_list: List[QApairs] = result.all()
        return result_list
    async def get_data_json_context(self,data:List[str],score:int):
        """获取json数据，有上下文"""
        statement = (
            select(
                QApairs.answer,
                QApairs.question.label("question"),
                Chunk.content.label("context"),
            )
            .select_from(QApairs)
            .join(Chunk, QApairs.chunk_id == Chunk.id, isouter=True)
            .where(QApairs.sole_uuid.in_(data))
        )
        result = await self.session.exec(statement)
        result_list:List[QApairs] = result.all()
        return result_list
    async def get_data_list(self,data:QAQueryTable):
        """获取list列表"""
        statement = select(QApairs).join(Books,Books.uuid==QApairs.sole_uuid).join(JoinLink,JoinLink.slave_id==Books.id)
        statement_count = select(func.count()).select_from(QApairs).join(Books,Books.uuid==QApairs.sole_uuid).join(JoinLink,JoinLink.slave_id==Books.id)
        # 动态拼接查询条件
        if data.keywords:
            statement = statement.where(QApairs.sole_uuid.like(f"{data.keywords}"))
            statement_count = statement_count.where(QApairs.sole_uuid.like(f"{data.keywords}"))
        if data.dataset_id:
            statement = statement.where(JoinLink.master_id==data.dataset_id)
            statement_count = statement_count.where(JoinLink.master_id==data.dataset_id)
        if data.books_id:
            statement = statement.where(JoinLink.slave_id == data.books_id)
            statement_count = statement_count.where(JoinLink.slave_id == data.books_id)
        statement = statement.order_by(QApairs.score and QApairs.id).limit(data.pagesize).offset(data.page_num)
        res = await self.session.exec(statement)
        total = await self.session.exec(statement_count)
        item = res.all()
        count = total.one()
        return TableData[QApairs](total=count,items=item).model_dump()
# 工厂函数
async def create_qa_pairs_db():
    async with async_session() as session:
        yield QApairsDB(session)
async def create_qa_pairs_load():
    async with async_session() as session:
        return QApairsDB(session)