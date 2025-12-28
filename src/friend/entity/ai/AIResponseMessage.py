from typing import List

from pydantic import BaseModel


class AIResponseMessage(BaseModel):
    knowledge_base_id:int
    message:str

class QuestionId(BaseModel):
    question:str
    id:int
    data_base:str
    collection:str

class QAPair(BaseModel):
    question:str
    answer:str

class GeneratedData(BaseModel):
    generated: List[QAPair]

class ScoreData(BaseModel):
    id:int
    score:int