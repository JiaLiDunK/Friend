import jwt
from fastapi import HTTPException
from fastapi import status
from fastapi.params import Depends
from fastapi.security import OAuth2PasswordBearer

from src.friend.config.SettingConfig import settings

oauth = OAuth2PasswordBearer(tokenUrl="/token")

# 验证JWT的依赖项
async def get_current_user(token:str=Depends(oauth)):
    credentials = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭证",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload =  jwt.decode(token,settings.SECRET_KEY,algorithms=[settings.ALGORITHM])
        username = payload.get("user_name")
        if username is None:
            raise credentials
    except jwt.PyJWTError :
        raise credentials
