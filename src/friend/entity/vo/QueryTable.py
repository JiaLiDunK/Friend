from pydantic import BaseModel, field_validator


class QueryTable(BaseModel):
    """分页查询"""
    pagesize: int
    page_num: int
    keywords: str

