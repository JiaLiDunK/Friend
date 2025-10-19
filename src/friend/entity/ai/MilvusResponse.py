from pydantic import BaseModel


class Entity(BaseModel):
    content:str

class SearchContent(BaseModel):
    id:int
    distance:float
    entity:Entity

class ContentId(BaseModel):
    id:int
    content:str


class SelectContent:
    def __init__(self, distance: float, id: int, content: str):
        self.distance = distance
        self.id = id
        self.content = content

    def __lt__(self, other):
        # Sort by distance in descending order (larger distance comes first)
        return self.distance > other.distance

    def __repr__(self):
        return f"SelectContent(distance={self.distance}, id={self.id}, content='{self.content[:50]}...')"
