from typing import List, Optional

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

class SelectDataByDataSet(BaseModel):
    selectedIds: List[int]
    scoreNum: Optional[int] = 0