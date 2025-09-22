from fastapi import APIRouter
from fastapi.params import Depends
from loguru import logger

from src.friend.app.db.PromptDB import PromptDB, create_prompt_db
from src.friend.entity.R import R
from src.friend.entity.po.MessagePrompt import MessagePrompt
from src.friend.entity.vo.QueryTable import QueryTable

messagePromptRouter = APIRouter()

@messagePromptRouter.post("/getPromptList")
async def get_prompt_list(
        data: QueryTable,
        prompt_db: PromptDB=Depends(create_prompt_db)
):
    logger.info(f"查询:{data}")
    data = await prompt_db.get_list(data)
    return R.ok().messages("查询成功").data_dict(data)

@messagePromptRouter.post("/insertPrompt")
async def insert_prompt(
        data: MessagePrompt,
        prompt_db: PromptDB=Depends(create_prompt_db)
):
    logger.info(f"插入数据:{data}")
    await prompt_db.insert_data(data)
    return R.ok().messages("新增成功")

@messagePromptRouter.post("/updatePrompt")
async def update_prompt(
        data: MessagePrompt,
        prompt_db: PromptDB=Depends(create_prompt_db)
):
    logger.info(f"修改数据:{data}")
    await prompt_db.update_data(data)
    return R.ok().messages("修改成功")