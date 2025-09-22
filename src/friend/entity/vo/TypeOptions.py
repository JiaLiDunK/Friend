from pydantic import BaseModel


class TypeOptions(BaseModel):
    value: int
    label: str