from datetime import datetime

import sqlalchemy.dialects.postgresql as postgresql
from sqlmodel import SQLModel, Field, Column


class FriendMessage(SQLModel,table=True):
    __tablename__ = "friend_message"
    id: int = Field(
        sa_column=Column(postgresql.INTEGER,
                         primary_key=True,
                         unique=True,
                         autoincrement=True),
    )
    type_id: int
    system_message: str
    user_id:int
    create_time:datetime
    version:int
    knowledge_owner_ids:int