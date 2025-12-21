from datetime import datetime

import sqlalchemy.dialects.postgresql as postgresql
from sqlmodel import SQLModel, Field, Column


class Dataset(SQLModel,table=True):
    __tablename__="dataset"
    id: int = Field(
        sa_column=Column(postgresql.INTEGER,
                         primary_key=True,
                         unique=True,
                         autoincrement=True),
    )
    description:str
    sole_uuid:str
    create_time:datetime