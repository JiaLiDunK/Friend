import sqlalchemy.dialects.postgresql as postgresql
from sqlmodel import SQLModel, Field, Column



class MessagePrompt(SQLModel):
    __tablename__ = "message_prompt"
    id: int = Field(
        sa_column=Column(postgresql.INTEGER,
                         primary_key=True,
                         unique=True,
                         autoincrement=True),
    )
    type_id: int
    system_message: str
    description: str