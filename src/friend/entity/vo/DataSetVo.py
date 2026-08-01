from pydantic import BaseModel


class DataSetVo(BaseModel):
    id: int
    description: str
    sole_uuid: str
    create_time: str
