from pydantic import BaseModel


class AIResponseMessage(BaseModel):
    knowledge_base_id:int
    message:str

class QuestionId(BaseModel):
    question:str
    id:int