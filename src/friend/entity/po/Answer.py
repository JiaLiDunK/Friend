from datetime import datetime

import sqlalchemy.dialects.postgresql as postgresql
from sqlmodel import SQLModel, Field, Column

class Answer(SQLModel,table=True):
    __tablename__ = "answer"
    id: int = Field(
        sa_column=Column(postgresql.INTEGER,
                         primary_key=True,
                         unique=True,
                         autoincrement=True),
    )
    uuid: str
    answer: str
    order: int
    create_time: datetime
    update_time: datetime