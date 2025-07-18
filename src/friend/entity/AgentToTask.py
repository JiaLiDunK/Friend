import sqlalchemy.dialects.postgresql as postgresql
from sqlmodel import SQLModel, Field, Column

class AgentToTask(SQLModel, table=True):
    id: int = Field(sa_column=Column(postgresql.INTEGER, primary_key=True, unique=True, autoincrement=True))
    agent_id: int
    task_id: int