import uuid
from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends

from src.friend.app.db.AnswerDB import AnswerDB, create_answer_db
from src.friend.app.db.QuestionDB import QuestionDB, create_question_db
from src.friend.entity.R import R
from src.friend.entity.po.Answer import Answer
from src.friend.entity.po.Question import Question
from src.friend.entity.vo.AddForm import AddFormQuestion
from loguru import logger
questionRouter = APIRouter()



@questionRouter.post("/insert")
async def add_question(data:AddFormQuestion,
                       question_db:QuestionDB=Depends(create_question_db),
                       answer_db:AnswerDB=Depends(create_answer_db)):
    logger.info(f"新增:{data}")
    now_date = datetime.now()
    u = str(uuid.uuid4())
    question = Question(uuid=u,create_time = now_date,
                        language_type=int(data.language),type_id=int(data.category),
                        power_id=int(data.power_id),question=data.question)
    answer_list:List[Answer] = []
    i = 1
    for item in data.answers:
        answer_list.append(Answer(uuid=u,create_time = now_date,
                        answer=item,order=i))
        i += 1
    await question_db.insert_data(question)
    await answer_db.insert_data_list(answer_list)
    return R.ok().messages("添加成功")
