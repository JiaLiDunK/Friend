from sqlmodel import select, func, update
from sqlmodel.ext.asyncio.session import AsyncSession

from src.friend.config.DBConfig import async_session
from src.friend.entity.po.MessagePrompt import MessagePrompt
from src.friend.entity.vo.QueryTable import QueryTable
from src.friend.entity.vo.TableData import TableData


class PromptDB:
    def __init__(self,session: AsyncSession):
        self.session = session
    async def __aenter__(self):
        self.session = async_session()
        await self.session.__aenter__()
        return PromptDB(self.session)

    async def __aexit__(self, exc_type, exc, tb):
        await self.session.__aexit__(exc_type, exc, tb)
    async def insert_data(self,data: MessagePrompt):
        """插入数据"""
        # type_id = 2先默认是2
        data.type_id = 2
        async with self.session.begin():
            self.session.add(data)
        return "添加成功"
    async def get_list(self,data: QueryTable):
        """获取书籍"""
        statement = select(MessagePrompt)
        count_statement = select(func.count()).select_from(MessagePrompt)
        # 动态拼接查询条件
        if data.keywords:
            statement = statement.where(MessagePrompt.system_message.like(f"%{data.keywords}%"))
            count_statement = count_statement.where(MessagePrompt.system_message.like(f"%{data.keywords}%"))
        statement = statement.limit(data.pagesize).offset(data.page_num).order_by(MessagePrompt.id)
        result = await self.session.exec(statement)
        total = await self.session.exec(count_statement)
        item = result.all()
        count = total.one()
        return TableData[MessagePrompt](total=count, items=item)
    async def update_data(self,data:MessagePrompt):
        """根据id修改数据"""
        async with self.session.begin():
            statement = update(MessagePrompt).where(MessagePrompt.id==data.id).values(type_id=data.type_id,system_message=data.system_message,description=data.description)
            await self.session.exec(statement)
    async def get_prompt_by_id(self,ids:int)->str:
        """根据id查询数据"""
        statement = select(MessagePrompt.system_message).where(MessagePrompt.id == ids)
        result = await self.session.exec(statement)
        item = result.one()
        return item


#工厂函数
async def create_prompt_db():
    async with async_session() as session:
        yield PromptDB(session)
async def create_prompt_db_by_load():
    async with async_session() as session:
        return PromptDB(session)