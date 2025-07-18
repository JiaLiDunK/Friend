import sqlalchemy.dialects.postgresql as postgresql
from sqlmodel import SQLModel, Field, Column

class Tasks(SQLModel, table=True):
    __tablename__ = "tasks"
    id: int = Field(sa_column=Column(postgresql.INTEGER, primary_key=True, unique=True, autoincrement=True))
    description: str
    expected_output: str
