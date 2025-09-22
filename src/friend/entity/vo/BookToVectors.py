from pydantic import BaseModel


class BookToVectors(BaseModel):
    id: int
    uuid: str
    knowledge_base_id: int
    type_id: int
    tittle: str