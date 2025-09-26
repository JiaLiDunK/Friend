from pydantic import BaseModel

class DataBaseState(BaseModel):
    message: str = ""