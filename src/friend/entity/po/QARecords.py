from datetime import datetime
from typing import Optional

import sqlalchemy.dialects.postgresql as postgresql
from sqlmodel import SQLModel, Field, Column


class QARecords(SQLModel, table=True):
    __tablename__ = "qa_records"

    id: Optional[int] = Field(
        default=None,
        sa_column=Column(
            postgresql.INTEGER,
            primary_key=True,
            autoincrement=True,
        ),
    )
    question: str = Field(max_length=2550)
    answer: str = Field(max_length=2550)
    context: Optional[str] = None
    insert_time: datetime = Field(default_factory=datetime.now)
    knowledge_base_id: Optional[int] = None