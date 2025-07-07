from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

from src.friend.config.SettingConfig import settings

# 创建引擎
async_engine = create_async_engine(
    url=settings.DATABASE_PG_URL,
    echo=True,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    future=True
)

# 只创建一次 sessionmaker
async_session_maker = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# 初始化数据库
async def init_db():
    """初始化数据库，创建所有的表"""
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

# 获取会话（数据访问）
async def get_session() -> AsyncSession:
    """异步生成器，提供数据库会话"""
    async with async_session_maker() as session:
        yield session

# （可选）事务支持
from contextlib import asynccontextmanager

@asynccontextmanager
async def get_transaction_session():
    """提供事务范围内的会话"""
    async with async_session_maker() as session:
        async with session.begin():
            yield session