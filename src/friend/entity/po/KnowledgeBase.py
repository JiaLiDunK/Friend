from typing import Optional

import sqlalchemy.dialects.postgresql as postgresql
from sqlmodel import SQLModel, Field, Column


class KnowledgeBase(SQLModel, table=True):
    __tablename__ = "knowledge_base"
    id: Optional[int] = Field(
        default=None,
        sa_column=Column(postgresql.INTEGER,
                         primary_key=True,
                         unique=True,
                         autoincrement=True),
    )
    data_base: str
    collection: str
    data_base_remark: str
    collection_remark: str
    type_id: int