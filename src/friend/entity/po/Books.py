from datetime import datetime

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
    tittle:str
    uuid:str
    type_id:int
    insert_time:datetime
    format:str
    use:str
    remark:str
    translate: int