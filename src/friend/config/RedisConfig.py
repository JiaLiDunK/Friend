import redis.asyncio as redis
from loguru import logger

from src.friend.config.SettingConfig import settings

redis_client: redis.Redis | None = None

async def init_redis():
    """初始化 Redis 连接"""
    global redis_client
    try:
        redis_client = redis.from_url(
            f"redis://{settings.REDIS_URL}:{settings.REDIS_PORT}",
            encoding="utf-8",
            decode_responses=True  # 自动解码为字符串
        )
        # ping一下验证连接
        await redis_client.ping()
        logger.info("redis已连接")
    except Exception as e:
        logger.error(f"redis连接失败: {e}")
        redis_client = None

async def close_redis():
    """关闭 Redis 连接"""
    global redis_client
    if redis_client:
        try:
            await redis_client.close()
            logger.info("redis已关闭")
        except Exception as e:
            logger.error(f"redis关闭失败: {e}")
        finally:
            redis_client = None