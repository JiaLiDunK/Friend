import uvicorn
from loguru import logger

from src.friend.config.SettingConfig import settings
from src.friend.app import app
# 配置日志文件
logger.add(settings.LOG_PATH, rotation="500 MB", encoding="utf-8",compression="zip", enqueue=True)
# 创建设置实例
if __name__ == '__main__':
    uvicorn.run(app,host=settings.HOST,port=settings.PORT,reload=True)