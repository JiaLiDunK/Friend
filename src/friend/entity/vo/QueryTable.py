from typing import List

from pydantic import BaseModel


class QueryTable(BaseModel):
    """分页查询"""
    pagesize: int
    page_num: int
    keywords: str

class SearchData(BaseModel):
    """检索"""
    question: str
    knowledge_base_id: int

class DownLoadJsonData(BaseModel):
    """下载json数据"""
    sole_uuid_list:List[str]
    score:int
