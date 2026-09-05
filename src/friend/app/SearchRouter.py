from fastapi import APIRouter, Depends
from langchain_ollama import OllamaLLM
from loguru import logger

from src.friend.agents.node.SearchNode import SearchNode, get_search_node
from src.friend.entity.R import R
from src.friend.entity.vo.QueryTable import SearchData

searchRouter = APIRouter()

@searchRouter.post("/send")
async def send(data:SearchData,search_node:SearchNode=Depends(get_search_node)):
    logger.info("搜索: {}",data)
    ollama = OllamaLLM(
        model="huihui_ai/qwen3-abliterated:8b",
        reasoning=True,
        temperature=0.2
    )
    message = await search_node.search_know_base(data)
    prompt = f"你是一个专业的信息归纳总结助手，麻烦总结下面的内容:{message}"
    data = await ollama.ainvoke(prompt)
    logger.info(f"ai进行总结的:{data}")
    return R.ok().messages("搜索成功").data_dict(data)
