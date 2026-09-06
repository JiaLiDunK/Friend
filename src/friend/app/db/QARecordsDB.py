from sqlmodel.ext.asyncio.session import AsyncSession

from src.friend.entity.po.QARecords import QARecords
from src.friend.config.DBConfig import async_session


class QARecordsDB:
    def __init__(self,session: AsyncSession):
        self.session = session
    async def __aenter__(self):
        self.session = async_session()
        await self.session.__aenter__()
        return QARecordsDB(self.session)

    async def __aexit__(self, exc_type, exc, tb):
        await self.session.__aexit__(exc_type, exc, tb)


    async def insert_one(self,data:QARecords):
        self.session.add(data)
        await self.session.commit()


async def create_qa_records_db():
    async with async_session() as session:
        yield QARecordsDB(session)
async def create_qa_records_db_by_load():
    async with async_session() as session:
        return QARecordsDB(session)