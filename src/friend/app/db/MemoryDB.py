from typing import List
from datetime import datetime
from sqlmodel import update, select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.friend.config.DBConfig import async_session
from src.friend.entity.po.Memory import Memory


class MemoryDB:
    def __init__(self,session:AsyncSession):
        self.session = session
    async def __aenter__(self):
        self.session = async_session()
        await self.session.__aenter__()
        return MemoryDB(self.session)

    async def __aexit__(self, exc_type, exc, tb):
        await self.session.__aexit__(exc_type, exc, tb)
    async def insert_data_ai(self,message:str,user_id:int):
        """插入ai数据"""
        data = Memory(
            user_id=user_id,
            type_id = 16,
            content = message,
            power = 18,
            del_flag = 2,
            create_time = datetime.now(),
            update_time = datetime.now()
        )
        await self.insert_data(data)
    async def insert_data_user(self,message:str,user_id:int):
        """插入用户数据"""
        data = Memory(
            user_id=user_id,
            type_id = 17,
            content = message,
            power = 18,
            del_flag = 2,
            create_time = datetime.now(),
            update_time = datetime.now()
        )
        await self.insert_data(data)
    async def insert_data(self,data:Memory):
        """插入数据"""
        self.session.add(data)
        await self.session.commit()
    async def get_short_term_ten_data(self,user_id:int)->List[Memory]:
        """获取改用户最近十次的聊天记录"""
        statement = select(Memory).where(Memory.user_id==user_id and Memory.is_deleted==21 and Memory.power==16).order_by(Memory.create_time.desc()).limit(10)
        result = await self.session.exec(statement)
        return result.all()
    async def get_mid_term_three_data(self,user_id:int)->List[Memory]:
        """获取改用户最近三次的聊天记录"""
        statement = select(Memory).where(Memory.user_id==user_id and Memory.is_deleted==21 and Memory.power==17).order_by(Memory.create_time.desc()).limit(3)
        result = await self.session.exec(statement)
        return result.all()
    async def get_long_term_one_data(self,user_id:int)->Memory:
        """获取改用户最近一次的聊天记录"""
        statement = select(Memory).where(Memory.user_id==user_id and Memory.is_deleted==21 and Memory.power==18).order_by(Memory.create_time.desc()).limit(1)
        result = await self.session.exec(statement)
        return result.one()
    async def del_data(self,id_list:List[int]):
        """逻辑上删除"""
        async with self.session.begin():
            statement = update(Memory).where(Memory.id.in_(id_list)).values(is_deleted=22)
            await self.session.exec(statement)



# 工厂函数
async def create_memory_db():
    async with async_session() as session:
        yield MemoryDB(session)
async def create_memory_db_by_load():
    async with async_session() as session:
        return MemoryDB(session)