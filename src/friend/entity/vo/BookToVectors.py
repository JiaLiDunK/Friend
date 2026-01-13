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

class DatasetToBook(BaseModel):
    id:int
    master_id:int
    master_name:str
    slave_name:str
    slave_id:int
    order_id:int
    sun_num:int

class JoinLinkBook(BaseModel):
    __tablename__="join_link"
    id: int
    master_id:int
    slave_id:int
    order_id:int
    sun_num:int
    scoring_completed:int
    tittle: str
