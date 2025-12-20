from typing import List

from pydantic import BaseModel


class AddFormQuestion(BaseModel):
    language: str
    category: str
    power_id: str
    question: str
    answers: List[str] = []

class AddBooks(BaseModel):
    path:str
    encode:str
    remark:str
    use:str