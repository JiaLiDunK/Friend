from fastapi import Depends
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from friend.config.DBConfig import get_session
from friend.entity.po.SysType import SysType


class TypeDB:
    def __init__(self,session: AsyncSession):
        self.session = session

    async def insert_type(self,type_data: SysType):
        """插入数据"""
        async with self.session.begin():
            data = await self.get_type_name(type_data.type_name)
            if data is not None:
                return "类型已存在"
            else:
                self.session.add(type_data)
                return "类型添加成功"


    async def get_type_name(self,type_name: str):
        """根据类型名字查看是否存在"""
        statement = select(SysType).where(SysType.type_name==type_name)
        result = await self.session.execute(statement)
        data = result.first()
        return data[0] if data else None

# 工厂函数
async def create_type_db(session: AsyncSession=Depends(get_session)) -> TypeDB:
    return TypeDB(session)