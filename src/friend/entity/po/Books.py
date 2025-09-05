import sqlalchemy.dialects.postgresql as postgresql
from sqlmodel import SQLModel, Field, Column


class Books(SQLModel,table=True):
    __tablename__="books"
    id: int = Field(
        sa_column=Column(postgresql.INTEGER,
                         primary_key=True,
                         unique=True,
                         autoincrement=True),
    )
    title:str
    uuid:str
    type_id:int