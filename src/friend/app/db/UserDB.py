from fastapi.params import Depends
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.friend.config.DBConfig import get_session
from src.friend.entity.SysUser import SysUser


class UserDB:
    def __init__(self,session: AsyncSession):
        self.session = session

    async def insert_user(self, user: SysUser) -> str:
        """插入数据"""
        async with self.session.begin():
            existing_user = await self.get_by_username(user.user_name)
            if existing_user is not None:
                return "用户已存在"
            else:
                self.session.add(user)
                return "注册成功"

    async def get_by_username(self,username: str) -> SysUser:
        """根据用户名查询数据库中是否存在了"""
        statement = select(SysUser).where(
            SysUser.user_name==username
        )
        # 执行查询并获取结果
        result = await self.session.execute(statement)
        user = result.first()
        return user[0] if user else None


# 工厂函数
async def create_user_db(session: AsyncSession=Depends(get_session)) -> UserDB:
    return UserDB(session)