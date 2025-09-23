from fastapi import APIRouter
from loguru import logger
chatRouter = APIRouter()


@chatRouter.post("/chatTest")
async def chat_test():
    logger.info("chatTest")
    return "chatTest"