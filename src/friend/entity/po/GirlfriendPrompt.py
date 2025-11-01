from datetime import datetime

import sqlalchemy.dialects.postgresql as postgresql
from sqlmodel import Field, Column, SQLModel


class GirlfriendPrompt(SQLModel,table=True):
    __tablename__ = "girlfriend_prompt"
    id: int = Field(
        sa_column=Column(postgresql.INTEGER,
                         primary_key=True,
                         unique=True,
                         autoincrement=True),
    )
    type_id: int
    prompt: str
    create_time: datetime
    user_id: int