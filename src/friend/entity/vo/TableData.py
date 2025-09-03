from typing import TypeVar, Generic, List

from pydantic import BaseModel

# 定义泛型
T = TypeVar("T")
class TableData(BaseModel,Generic[T]):
    total: int
    items: List[T]