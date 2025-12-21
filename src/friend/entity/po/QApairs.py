from datetime import datetime

import sqlalchemy.dialects.postgresql as postgresql
from sqlmodel import SQLModel, Field, Column


class QApairs(SQLModel,table=True):
    __tablename__="qa_pairs"
    id: int = Field(
        sa_column=Column(postgresql.INTEGER,
                         primary_key=True,
                         unique=True,
                         autoincrement=True),
    )
    chunk_id:int
    question:str
    answer:str
    order_id:int
    insert_time:datetime
    sole_uuid:str
