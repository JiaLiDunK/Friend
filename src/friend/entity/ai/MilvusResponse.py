from pydantic import BaseModel


class Entity(BaseModel):
    content:str

class SearchContent(BaseModel):
    id:int
    distance:float
    entity:Entity