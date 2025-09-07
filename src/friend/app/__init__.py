from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.params import Depends
from loguru import logger
from starlette.middleware.cors import CORSMiddleware

from src.friend.app.MessagePromptRouter import messagePromptRouter
from src.friend.app.ReadAndOutRouter import readAndOutRouter
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
# 配置容许的前端域名
origins = [
    'http://127.0.0.1:7000',
    'http://localhost:7000'
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(userRouter,prefix="/user",tags=["用户"])
app.include_router(typeRouter,prefix="/type",tags=["类型"])
app.include_router(messagePromptRouter,prefix="/prompt",tags=["提示词"])
app.include_router(readAndOutRouter,prefix="/readAndOut",tags=["读取与输出"])
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