import sqlalchemy.dialects.postgresql as postgresql
from sqlmodel import SQLModel, Field, Column

class JoinLink(SQLModel,table=True):
    __tablename__="join_link"
    id: int = Field(
        sa_column=Column(postgresql.INTEGER,
                         primary_key=True,
                         unique=True,
                         autoincrement=True),
    )
    master_id:int
    slave_id:int
    order_id:int
    sun_num:int
    score:int
    scoring_completed:int
