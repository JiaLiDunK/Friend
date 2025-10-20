from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from src.friend.config.SettingConfig import settings

async_engine = create_async_engine(
    url=settings.DATABASE_PG_URL,
    echo=True,
    pool_size=10,  # 最大连接数
    max_overflow=20,  # 超出 pool_size 后还能额外创建的连接
    pool_timeout=30,  # 获取连接超时时间
    pool_recycle=1800,  # 定时回收连接（秒），防止长连接失效
    pool_pre_ping=True
)
async_session = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)
async def init_db():
    """初始化数据库，创建所有的表"""
    async with async_engine.begin() as connection:
        await connection.run_sync(SQLModel.metadata.create_all)

@asynccontextmanager
async def get_session() -> AsyncSession:
    session = async_session()
    try:
        yield session
        await session.commit()   # 正常就提交
    except Exception:
        await session.rollback() # 出错就回滚
        raise
    finally:
        await session.close()    # 一定回收连接


