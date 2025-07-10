from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from src.friend.config.SettingConfig import settings

async_engine = create_async_engine(
    url=settings.DATABASE_PG_URL,
    echo=True,
    pool_pre_ping=True
)

async def init_db():
    """初始化数据库，创建所有的表"""
    async with async_engine.begin() as connection:
        await connection.run_sync(SQLModel.metadata.create_all)

async def get_session() -> AsyncSession:
    """创建并返回一个异步数据库会话"""
    async_session = sessionmaker(
        bind=async_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    async with async_session() as session:
        yield session


