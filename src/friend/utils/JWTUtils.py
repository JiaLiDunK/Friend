import time

import jwt

from src.friend.config.SettingConfig import settings


async def create_access_token(data: dict):
    """创建jwt"""
    to_encode = data.copy()
    to_encode.update({"exp":time.time()+settings.ACCESS_TOKEN_EXPIRE_MINUTES})
    encode_jwt = jwt.encode(to_encode,settings.SECRET_KEY,algorithm=settings.ALGORITHM)
    return encode_jwt