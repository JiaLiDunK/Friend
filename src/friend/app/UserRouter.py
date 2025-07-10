import hashlib
from datetime import datetime
from fastapi.params import Depends
from fastapi.routing import APIRouter
from pydantic import BaseModel, field_validator
from loguru import logger
from src.friend.app.db.UserDB import UserDB, create_user_db
from src.friend.entity.SysUser import SysUser
from src.friend.utils.JWTUtils import create_access_token
from src.friend.utils.StringUtils import generate_random_string

userRouter = APIRouter()

class UserRegister(BaseModel):
    """用户注册"""
    user_name: str
    password: str
    nick_name: str
    @field_validator("user_name",'nick_name','password')
    def check_user_name(cls, v, field):
        if not v or not v.strip():
            raise ValueError(f"用户名:{field}不能为空")
        length = len(v.strip())
        if length < 3:
            raise ValueError("用户名长度不能少于3个字符")
        if length > 20:
            raise ValueError("用户名长度不能超过20个字符")
        return v

class UserLogin(BaseModel):
    """用户注册"""
    user_name: str
    password: str
    @field_validator("user_name",'password')
    def check_user_name(cls, v, field):
        if not v or not v.strip():
            raise ValueError(f"用户名:{field}不能为空")
        length = len(v.strip())
        if length < 3:
            raise ValueError("用户名长度不能少于3个字符")
        if length > 20:
            raise ValueError("用户名长度不能超过20个字符")
        return v

@userRouter.post("/register")
async def register(data: UserRegister,
               userdb: UserDB = Depends(create_user_db)) -> str:
    """注册"""
    logger.info("用户注册:",data.user_name)
    salt = await generate_random_string()
    password = data.password + salt
    password = hashlib.sha256(password.encode("utf-8")).hexdigest()
    users = SysUser(
        user_name=data.user_name,
        password=password,
        salt=salt,
        nick_name=data.nick_name,
        create_time=datetime.now()
    )
    result = await userdb.insert_user(users)
    return result

@userRouter.post("/login")
async def login(data: UserLogin,
                userdb: UserDB = Depends(create_user_db)):
    """登录"""
    user: SysUser = await userdb.get_by_username(data.user_name)
    if user is None:
        return {"message": "用户不存在"}
    password = data.password + user.salt
    password = hashlib.sha256(password.encode("utf-8")).hexdigest()
    if password != user.password:
        return {"message": "密码错误"}
    else:
        jwt = await create_access_token({
            "user_name": user.user_name,
            "password": user.password,
            "id": user.id
        })
        return jwt