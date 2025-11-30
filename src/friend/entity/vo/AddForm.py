from typing import List

from pydantic import BaseModel


class AddFormQuestion(BaseModel):
    language: str
    category: str
    power_id: str
    question: str
    answers: List[str] = []