from datetime import time, datetime
from typing import Optional

import sqlalchemy.dialects.postgresql as postgresql
from sqlmodel import SQLModel, Field, Column


class LlmCallLogs(SQLModel, table=True):
    __tablename__ = "llm_call_logs"
    id: Optional[int] = Field(
        default=None,
        sa_column=Column(postgresql.INTEGER,
                         primary_key=True,
                         autoincrement=True),
    )
    input_tokens:int
    output_tokens:int
    total_tokens:int
    create_time:datetime
    model_name:str
    status:int
    function_name:str
    error_message:str
    call_type:int
    elapsed_time:float
    uuid:str