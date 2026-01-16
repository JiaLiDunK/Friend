from typing import List

from pydantic import BaseModel


class QueryTable(BaseModel):
    """分页查询"""
    pagesize: int
    page_num: int
    keywords: str = None
    key_num: int = None

class SearchData(BaseModel):
    """检索"""
    question: str
    knowledge_base_id: int

class DownLoadJsonData(BaseModel):
    """下载json数据"""
    id_list:List[int]
    score:int

class QAQueryTable(BaseModel):
    """分页查询"""
    pagesize: int
    page_num: int
    keywords: str = None
    key_num: int = None
    dataset_id:int = None
    books_id: int = None
