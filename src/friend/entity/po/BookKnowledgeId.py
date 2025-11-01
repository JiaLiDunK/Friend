import sqlalchemy.dialects.postgresql as postgresql
from sqlmodel import Field, Column

class BookKnowledgeId:
    __tablename__ = "book_knowledge_id"
    id: int = Field(
        sa_column=Column(postgresql.INTEGER,
                         primary_key=True,
                         unique=True,
                         autoincrement=True),
    )
    book_vectors_id: int
    knowledge_base_id: int
    type_id: int