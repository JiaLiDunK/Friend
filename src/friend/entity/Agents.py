import sqlalchemy.dialects.postgresql as postgresql
from sqlmodel import SQLModel, Field, Column


class Agents(SQLModel,table=True):
    __tablename__ = "agents"
    id: int = Field(sa_column=Column(postgresql.INTEGER, primary_key=True, unique=True, autoincrement=True)),
    role: str
    goal: str
    backstory: str
    remarks: str