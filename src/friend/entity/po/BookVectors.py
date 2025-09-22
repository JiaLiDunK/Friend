import sqlalchemy.dialects.postgresql as postgresql
from sqlmodel import SQLModel, Field, Column

class BookVectors(SQLModel,table=True):
    __tablename__="book_vectors"
    id: int = Field(
        sa_column=Column(postgresql.INTEGER,
                         primary_key=True,
                         unique=True,
                         autoincrement=True),
    )
    uuid: str = Field(foreign_key="books.uuid")
    knowledge_base_id: int
    type_id: int