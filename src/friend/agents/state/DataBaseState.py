from langchain_core.messages import BaseMessage
from pydantic import BaseModel

class DataBaseState(BaseModel):
    message: BaseMessage