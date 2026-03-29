from pydantic import BaseModel
from datetime import datetime

class DataSetVo(BaseModel):
    id: int
    description: str
    sole_uuid: str
    create_time: str
