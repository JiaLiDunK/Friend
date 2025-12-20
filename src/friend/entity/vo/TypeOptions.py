from pydantic import BaseModel


class TypeOptions(BaseModel):
    value: int
    label: str

class SelectOptions(BaseModel):
    master_id: int
    slave_id: int
    uuid:str