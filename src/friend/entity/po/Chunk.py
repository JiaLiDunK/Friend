import sqlalchemy.dialects.postgresql as postgresql
from sqlmodel import SQLModel, Field, Column


class Chunk(SQLModel,table=True):
    __tablename__="chunk"
    id: int = Field(
        sa_column=Column(postgresql.INTEGER,
                         primary_key=True,
                         unique=True,
                         autoincrement=True),
    )
    content:str
    order_id:int
    title_id:int
    uuid:str
    type_id:int