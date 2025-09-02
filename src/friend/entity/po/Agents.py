import sqlalchemy.dialects.postgresql as postgresql
from sqlmodel import SQLModel, Field, Column


class Agents(SQLModel,table=True):
    __tablename__ = "sys_type"
    id: int = Field(
        sa_column=Column(postgresql.INTEGER,
                         primary_key=True,
                         unique=True,
                         autoincrement=True),
    )
    role: str
    backstory: str
    goal: str
    description: str
    output: str