import asyncio

import jwt

from src.friend.config.SettingConfig import settings
from src.friend.utils.JWTUtils import create_access_token


if __name__ == '__main__':

    data = {
        "user_name": "admin",
        "password": "123456",
        "nick_name": "admin"
    }
    token = asyncio.run(create_access_token(data))
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    print(token)
    print(payload.get("user_name"))