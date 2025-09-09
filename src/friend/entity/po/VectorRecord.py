import sqlalchemy.dialects.postgresql as postgresql
from sqlmodel import SQLModel, Field, Column


class VectorRecord(SQLModel, table=True):
    __tablename__ = "vector_record"
    id: int = Field(
        sa_column=Column(postgresql.INTEGER,
                         primary_key=True,
                         unique=True,
                         autoincrement=True),
    )
    tittle: str
    knowledge_base_id: int
    uuid: str
