import sqlalchemy.dialects.postgresql as postgresql
from sqlmodel import SQLModel, Field, Column

class PromptKnowledge(SQLModel,table=True):
    __tablename__ = "prompt_knowledge"
    id: int = Field(
        sa_column=Column(postgresql.INTEGER,
                         primary_key=True,
                         unique=True,
                         autoincrement=True),
    )
    prompt_id: int
    knowledge_id: int
    type_id: int
    remark: str