import hashlib
from datetime import datetime

from fastapi.params import Depends
from fastapi.routing import APIRouter
from loguru import logger
from src.friend.app.db.UserDB import UserDB, create_user_db
from src.friend.entity.R import R
from src.friend.entity.po.SysUser import SysUser
from src.friend.entity.vo.User import User
from src.friend.entity.vo.UserLogin import UserLogin
from src.friend.entity.vo.UserRegister import UserRegister
from src.friend.utils.JWTUtils import create_access_token
from src.friend.utils.StringUtils import generate_random_string

userRouter = APIRouter()



@userRouter.post("/register")
async def register(data: UserRegister,
               user_db: UserDB = Depends(create_user_db)) -> R:
    """注册"""
    logger.info("用户注册:",data.username)
    return R.error().messages("暂时不支持注册")
    salt = await generate_random_string()
    password = data.password + salt
    password = hashlib.sha256(password.encode("utf-8")).hexdigest()
    users = SysUser(
        user_name=data.name,
        password=password,
        salt=salt,
        email=data.email,
        create_time=datetime.now()
    )
    result = await user_db.insert_user(users)
    return R.error(result)

@userRouter.post("/login")
async def login(data: UserLogin,
                user_db: UserDB = Depends(create_user_db))->R:
    """登录"""
    logger.info(f"登录中:{data.email}")
    user: SysUser = await user_db.get_by_email(data.email)
    if user is None:
        return R.error().code_value(300).messages("用户不存在")
    password = data.password + user.salt
    password = hashlib.sha256(password.encode("utf-8")).hexdigest()
    if password != user.password:
        return R.error().messages("密码错误")
    else:
        jwt = await create_access_token({
            "email": user.email,
            "password": user.password,
            "id": user.id
        })
        return R.ok().jwt_value(jwt).data_dict(User(id=user.id,email=user.email,name=user.user_name,role="普通"))

