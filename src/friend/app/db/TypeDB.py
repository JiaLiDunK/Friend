from sqlmodel import select, func, update
from sqlmodel.ext.asyncio.session import AsyncSession

from src.friend.config.DBConfig import async_session
from src.friend.entity.po.SysType import SysType
from src.friend.entity.vo.QueryTable import QueryTable
from src.friend.entity.vo.TableData import TableData


class TypeDB:
    def __init__(self,session: AsyncSession):
        self.session = session
    async def __aenter__(self):
        self.session = async_session()
        await self.session.__aenter__()
        return TypeDB(self.session)

    async def __aexit__(self, exc_type, exc, tb):
        await self.session.__aexit__(exc_type, exc, tb)
    async def insert_type(self,type_data: SysType):
        """插入数据"""
        data = await self.get_type_name(type_data.type_name)
        if data is not None:
            return "类型已存在"
        else:
            # 移除 id，防止手动传入重复主键
            type_data.id = None
            self.session.add(type_data)
            await self.session.commit()
        return "类型添加成功"


    async def get_type_name(self,type_name: str):
        """根据类型名字查看是否存在"""
        statement = select(SysType).where(SysType.type_name==type_name)
        result = await self.session.exec(statement)
        data = result.first()
        return data if data else None

    async def get_type_list(self,data: QueryTable):
        """根据参数查询数据库"""
        statement = select(SysType)
        count_statement = select(func.count()).select_from(SysType)
        # 动态拼接查询条件
        if data.keywords:
            statement = statement.where(SysType.type_name.like(f"%{data.keywords}%"))
            count_statement = count_statement.where(SysType.type_name.like(f"%{data.keywords}%"))
        statement = statement.order_by(SysType.id).limit(data.pagesize).offset(data.page_num)
        result = await self.session.exec(statement)
        total = await self.session.exec(count_statement)
        item = result.all()
        count = total.one()
        return TableData[SysType](total=count, items=item)
    async def update_type(self,type_data: SysType):
        """修改数据"""
        async with self.session.begin():
            statement = update(SysType).where(SysType.id==type_data.id).values(type_name=type_data.type_name)
            await self.session.exec(statement)


# 工厂函数
async def get_type_db():
    async with async_session() as session:
        yield TypeDB(session)
async def get_type_db_by_load():
    async with async_session() as session:
        return TypeDB(session)