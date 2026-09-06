from cleo.ui import question
from fastapi import APIRouter, Depends
from langchain_ollama import OllamaLLM
from loguru import logger

from src.friend.app.db.PromptDB import create_prompt_db, PromptDB
from src.friend.app.db.QARecordsDB import create_qa_records_db, QARecordsDB
from src.friend.entity.po.QARecords import QARecords
from src.friend.agents.node.SearchNode import SearchNode, get_search_node
from src.friend.entity.R import R
from src.friend.entity.vo.QueryTable import SearchData

searchRouter = APIRouter()

@searchRouter.post("/send")
async def send(data:SearchData,search_node:SearchNode=Depends(get_search_node),
               qa_record_db:QARecordsDB=Depends(create_qa_records_db),
               prompt_db: PromptDB = Depends(create_prompt_db)):
    logger.info("搜索: {}",data)
    ollama = OllamaLLM(
        model="huihui_ai/qwen3-abliterated:8b",
        reasoning=True,
        temperature=0.2
    )
    message = await search_node.search_know_base(data)
    prompt = await prompt_db.get_prompt_by_id(10)
    data_re = await ollama.ainvoke(prompt.format(message=message,question=data.question))
    qa_record = QARecords(question=data.question,answer=data_re,context=message,knowledge_base_id=data.knowledge_base_id)
    await qa_record_db.insert_one(qa_record)
    return R.ok().messages("搜索成功").data_dict(data_re)
