from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.friend.config.DBConfig import async_session
from src.friend.entity.po.SysUser import SysUser


class UserDB:
    def __init__(self,session: AsyncSession):
        self.session = session

    async def __aenter__(self):
        self.session = async_session()
        await self.session.__aenter__()
        return UserDB(self.session)

    async def __aexit__(self, exc_type, exc, tb):
        await self.session.__aexit__(exc_type, exc, tb)

    async def insert_user(self, user: SysUser) -> str:
        """插入数据"""
        existing_user = await self.get_by_email(user.email)
        if existing_user is not None:
            return "用户已存在"
        else:
            async with self.session.begin():
                self.session.add(user)
        return "注册成功"

    async def get_by_email(self,email: str) -> SysUser:
        """根据用户名查询数据库中是否存在了"""
        statement = select(SysUser).where(
            SysUser.email==email
        )
        # 执行查询并获取结果
        result = await self.session.exec(statement)
        user = result.first()
        return user[0] if user else None


# 工厂函数  如果milvus开启多线程查询,可能需要改成这种写法
async def create_user_db():
    async with async_session() as session:
        yield UserDB(session)
async def create_user_db_by_load():
    async with async_session() as session:
        return UserDB(session)