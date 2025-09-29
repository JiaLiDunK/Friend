from pydantic import BaseModel

from src.friend.entity.po.BookVectors import BookVectors


class BookToVectors(BaseModel):
    tittle: str
    id: int
    uuid: str
    type_id: int
    knowledge_base_id: int

    @classmethod
    def from_orm_join(cls, bv: BookVectors, tittle: str):
        return cls(
            id=bv.id,
            uuid=bv.uuid,
            type_id=bv.type_id,
            knowledge_base_id=bv.knowledge_base_id,
            tittle=tittle,
        )