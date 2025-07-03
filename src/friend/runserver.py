import uvicorn
from src.friend.config.SettingConfig import settings
from loguru import logger

# 配置日志文件
logger.add("logs/friend.log", rotation="500 MB", encoding="utf-8",compression="zip", enqueue=True)
# 创建设置实例
if __name__ == '__main__':
    uvicorn.run("app:app",host=settings.HOST,port=settings.PORT,reload=True)