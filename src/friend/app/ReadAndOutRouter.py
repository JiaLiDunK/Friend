
import logging

from fastapi import APIRouter

from src.friend.agents.node.ReadNode import ReadNode

readAndOutRouter = APIRouter()

@readAndOutRouter.post("/read")
async def read_and_out(path: str):
    logging.info(f"读取的路径{path}")
    reading = await ReadNode.create()
    await reading.read_path(path)
    return "处理完成"
