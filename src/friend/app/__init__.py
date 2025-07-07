from contextlib import asynccontextmanager

import jwt
from fastapi import FastAPI, HTTPException, status, Request
from fastapi.params import Depends
from fastapi.security import OAuth2PasswordBearer
from loguru import logger
from starlette.responses import RedirectResponse

from src.friend.app.UserRouter import userRouter
from src.friend.config.SettingConfig import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("服务器启动中")
    yield
    logger.info("服务器关闭中")

oauth = OAuth2PasswordBearer(tokenUrl="/token")

app = FastAPI(
    title="基础环境的搭建",
    version="1.0",
    deprecation="开始搭建自己的python基础服务",
    lifespan=lifespan,
)
app.include_router(userRouter,prefix="/user",tags=["用户"])

# 验证JWT的依赖项
async def get_current_user(token:str=Depends(oauth)):
    credentials = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭证",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload =  jwt.decode(token,settings.SECRET_KEY,algorithms=[settings.ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials
    except jwt.PyJWTError :
        raise credentials
    # user = get_user()
    return {"username": username}
# 未授权时重定向用户
@app.middleware("http")
async def redirect_unauthorized(request: Request, call_next):
    # 开放的
    open_routes = ['/user',]
    if request.url.path in open_routes:
        return await call_next(request)
    else:
        response = await call_next(request)
        if response.status_code == status.HTTP_401_UNAUTHORIZED:
            return RedirectResponse(url="/login")
    return response


# 登录测试
@app.get("/login")
async def login():
    return {"message": "请先登录"}

# 测试
@app.get('/test')
async def test(current_user: str = Depends(get_current_user)):
    return {"message": "Hello, World!::"}


