import sqlalchemy.dialects.postgresql as postgresql
from sqlmodel import SQLModel, Field, Column


class ClearChunk(SQLModel,table=True):
    __tablename__="clear_chunk"
    id: int = Field(
        sa_column=Column(postgresql.INTEGER,
                         primary_key=True,
                         unique=True,
                         autoincrement=True),
    )
    type_id: int
    content: str
    chunk_id: int
    order_id: int