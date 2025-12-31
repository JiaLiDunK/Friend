from typing import List

from sqlalchemy import func, update

from src.friend.entity.po.Chunk import Chunk
from src.friend.entity.vo.QueryTable import DownLoadJsonData, QueryTable
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from src.friend.config.DBConfig import async_session
from src.friend.entity.po.QApairs import QApairs
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
    async def get_data_json(self,data:DownLoadJsonData):
        """获取json数据"""
        statement = select(QApairs).where(QApairs.sole_uuid.in_(data.sole_uuid_list))
        if data.score is not None or data.score != 0 :
            statement = statement.where(QApairs.score>=data.score)
        result = await self.session.exec(statement)
        result_list:List[QApairs] = result.all()
        return result_list
    async def get_data_json_context(self,data:DownLoadJsonData):
        """获取json数据，有上下文"""
        statement = (select(QApairs.answer,
                            ("context:"+Chunk.content+" ;"+QApairs.question).label("question"),
                            Chunk.content)
                     .join(Chunk, QApairs.sole_uuid == Chunk.uuid).
        where(QApairs.sole_uuid.in_(data.sole_uuid_list)))
        if data.score is not None and data.score != 0:
            statement = statement.where(QApairs.score == data.score)
        result = await self.session.exec(statement)
        result_list:List[QApairs] = result.all()
        return result_list
    async def get_data_list(self,data:QueryTable):
        """获取list列表"""
        statement = select(QApairs)
        statement_count = select(func.count()).select_from(QApairs)
        # 动态拼接查询条件
        if data.keywords:
            statement = statement.where(QApairs.sole_uuid.like(f"{data.keywords}"))
            statement_count = statement_count.where(QApairs.sole_uuid.like(f"{data.keywords}"))
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