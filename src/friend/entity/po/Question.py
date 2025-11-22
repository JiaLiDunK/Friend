from datetime import datetime

import sqlalchemy.dialects.postgresql as postgresql
from sqlmodel import SQLModel, Field, Column

class Question(SQLModel,table=True):
    __tablename__ = "question"
    id: int = Field(
        sa_column=Column(postgresql.INTEGER,
                         primary_key=True,
                         unique=True,
                         autoincrement=True),
    )
    question: str
    language_type: int
    type_id: int
    uuid: str
    power_id: int
    create_time: datetime
    update_time: datetime