from pydantic import BaseModel

from src.friend.entity.po.BookKnowledgeId import BookKnowledgeId
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
class KnowledgeToBook(BaseModel):
    tittle: str
    id: int
    type_id: int
    uuid: str
    data_base_remark: str
    collection_remark: str
    knowledge_base_id: int

    @classmethod
    def from_orm_join(cls, bv: BookKnowledgeId, tittle: str,data_base_remark: str,
    collection_remark: str):
        return cls(
            id=bv.id,
            uuid=bv.uuid,
            type_id=bv.type_id,
            knowledge_base_id=bv.knowledge_base_id,
            tittle=tittle,
            data_base_remark=data_base_remark,
            collection_remark=collection_remark
        )