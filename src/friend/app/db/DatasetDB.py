from src.friend.entity.vo.TableData import TableData
from sqlalchemy import func, update
from sqlmodel import select
from src.friend.entity.vo.QueryTable import QueryTable
from src.friend.entity.po.dataset import Dataset
from sqlmodel.ext.asyncio.session import AsyncSession

from src.friend.config.DBConfig import async_session


class DatasetDB:
    def __init__(self,session: AsyncSession):
        self.session = session
    async def __aenter__(self):
        self.session = async_session()
        await self.session.__aenter__()
        return DatasetDB(self.session)

    async def __aexit__(self, exc_type, exc, tb):
        await self.session.__aexit__(exc_type, exc, tb)
    async def insert_data(self,data:Dataset)->str:
        """添加单个数据"""
        self.session.add(data)
        await self.session.commit()
        return "添加成功"
    async def del_data(self,data:Dataset)->str:
        """删除单个数据"""
        await self.session.delete(data)
        await self.session.commit()
        return "删除成功"
    async def get_data_list(self,data:QueryTable):
        """获取根据条件获取书籍的内容"""
        statement = select(Dataset)
        count_statement = select(func.count()).select_from(Dataset)
        # 动态拼接查询条件
        if data.keywords:
            statement = statement.where(Dataset.description.like(f"%{data.keywords}%"))
            count_statement = count_statement.where(Dataset.description.like(f"%{data.keywords}%"))
        statement = statement.order_by(Dataset.id).limit(data.pagesize).offset(data.page_num)
        result = await self.session.exec(statement)
        total = await self.session.exec(count_statement)
        item = result.all()
        count = total.one()
        dataset_list = [Dataset.model_validate(dataset) for dataset in item]
        return TableData[Dataset](total=count,items=dataset_list).model_dump()
    async def update_data(self,data:Dataset)->str:
        """更新单个数据"""
        statement = update(Dataset).where(Dataset.id==data.id).values(description=data.description)
        await self.session.exec(statement)
        await self.session.commit()
        return "更新成功"
# 工厂函数
async def create_dataset_db():
    async with async_session() as session:
        yield DatasetDB(session)
async def create_dataset_load():
    async with async_session() as session:
        return DatasetDB(session)