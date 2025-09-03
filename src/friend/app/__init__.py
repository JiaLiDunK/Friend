from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.params import Depends
from loguru import logger

from src.friend.app.TypeRouter import typeRouter
from src.friend.app.UserRouter import userRouter
from src.friend.config.SecurityConfig import get_current_user


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("服务器启动中")
    yield
    logger.info("服务器关闭中")


app = FastAPI(
    title="基础环境的搭建",
    version="1.0",
    deprecation="开始搭建自己的python基础服务",
    lifespan=lifespan,
)
app.include_router(userRouter,prefix="/user",tags=["用户"])
app.include_router(typeRouter,prefix="/type",tags=["类型"])

# 未授权时重定向用户
# @app.middleware("http")
# async def redirect_unauthorized(request: Request, call_next):
#     # 开放的
#     open_routes = ['/user/register',]
#     if request.url.path in open_routes:
#         return await call_next(request)
#     else:
#         response = await call_next(request)
#         if response.status_code == status.HTTP_401_UNAUTHORIZED:
#             return RedirectResponse(url="/user/register")
#     return response


# 测试
@app.get('/test')
async def test(current_user: str = Depends(get_current_user)):
    print("开始1:",current_user)
    return {"message": "Hello, World!::"}

# 测试
@app.get('/test1')
async def test1():
    return {"message": "Hello, World!::111"}