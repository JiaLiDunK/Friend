import hashlib

from fastapi.params import Depends
from fastapi.routing import APIRouter
from pydantic import BaseModel

from src.friend.app.db.UserDB import UserDB, create_user_db
from src.friend.utils.StringUtils import generate_random_string

userRouter = APIRouter()

class UserRegister(BaseModel):
    """用户注册"""
    username: str
    password: str

@userRouter.post("/register")
async def user(data: UserRegister,
               userdb: UserDB = Depends(create_user_db)) -> str:
    """注册"""
    salt = await generate_random_string()
    password = data.password + salt
    password = hashlib.sha256(password.encode("utf-8")).hexdigest()
    print(password)
    print(userdb.test())
    return "ok"
