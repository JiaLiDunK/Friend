from pydantic import BaseModel, field_validator


class QueryTable(BaseModel):
    """分页查询"""
    pagesize: int
    page_num: int
    keywords: str
    @field_validator("keywords","page_num","pagesize")
    def check_value(cls, v, field):
        if not v or not v.strip():
            raise ValueError(f"{field}不能为空")
        return v
