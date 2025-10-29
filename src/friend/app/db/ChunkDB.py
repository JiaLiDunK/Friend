from typing import List

from sqlalchemy import func, update, delete
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from src.friend.config.DBConfig import async_session
from src.friend.entity.po.Chunk import Chunk
from src.friend.entity.vo.QueryTable import QueryTable
from src.friend.entity.vo.TableData import TableData


class ChunkDB:
    def __init__(self,session: AsyncSession):
        self.session = session
    async def __aenter__(self):
        self.session = async_session()
        await self.session.__aenter__()
        return ChunkDB(self.session)

    async def __aexit__(self, exc_type, exc, tb):
        await self.session.__aexit__(exc_type, exc, tb)
    async def insert_list(self,data_list:List[Chunk]):
        """批量插入数据"""
        async with self.session.begin():
            self.session.add_all(data_list)

    async def get_data_list(self,data:QueryTable):
        """根据uuid获取数据"""
        statement = select(Chunk).where(Chunk.uuid == data.keywords).order_by(Chunk.order_id).limit(
            data.pagesize).offset(data.page_num)
        count_statement = select(func.count()).select_from(Chunk).where(Chunk.uuid == data.keywords)
        result = await self.session.exec(statement)
        total = await self.session.exec(count_statement)
        item = result.all()
        count = total.one()
        return TableData[Chunk](total=count, items=item).model_dump()
    async def update_data(self,data:Chunk):
        """更新数据"""
        async with self.session.begin():
            statement = update(Chunk).where(Chunk.id==data.id).values(content=data.content,type_id=data.type_id)
            await self.session.exec(statement)
    async def select_all_uuid(self):
        """查询所有的uuid"""
        statement = select(Chunk.uuid).distinct()
        result = await self.session.exec(statement)
        return result.all()
    async def del_uuid(self,uuid:str):
        """根据uuid删除"""
        async with self.session.begin():
            statement = delete(Chunk).where(Chunk.uuid==uuid)
            await self.session.exec(statement)
    async def get_data_uuid(self,uuid:str):
        """根据uuid获取所有的内容"""
        statement = select(Chunk).where(Chunk.uuid == uuid)
        result = await self.session.exec(statement)
        return result.all()
    async def update_data_list(self,data_list:List[Chunk]):
        """批量修改内容"""
        for data in data_list:
            statement = (
                update(Chunk)
                .where(Chunk.id == data.id)
                .values(content=data.content)
            )
            await self.session.exec(statement)
    async def del_data_and_save(self,data_list:List[Chunk],uuid:str):
        """删除旧数据并保存新数据"""
        async with self.session.begin():
            statement = delete(Chunk).where(Chunk.uuid==uuid)
            await self.session.exec(statement)
            self.session.add_all(data_list)

    async def get_content_by_uuid(self, uuid: str):
        """根据uuid获取所有的内容"""
        statement = select(Chunk.content).where(Chunk.uuid == uuid)
        result = await self.session.exec(statement)
        return result.all()

# 工厂函数（业务内部调用用这个）
async def create_chunk_db():
    async with async_session() as session:
        yield ChunkDB(session)
# 这个是给切割文档用的
async def create_chunk_db_by_load():
    async with async_session() as session:
        return ChunkDB(session)