from datetime import datetime
from typing import Optional

import sqlalchemy.dialects.postgresql as postgresql
from sqlmodel import SQLModel, Field, Column


class Memory(SQLModel,table=True):
    __tablename__ = "memory"
    id: Optional[int] = Field(
        default=None,
        sa_column=Column(postgresql.INTEGER,
                         primary_key=True,
                         autoincrement=True),
    )
    user_id: int
    type_id: int
    content: str
    power: int
    del_flag: int
    create_time: datetime