from pydantic import BaseModel, field_validator


class UserLogin(BaseModel):
    """用户注册"""
    email: str
    password: str
    @field_validator("email",'password')
    def check_email(cls, v, field):
        if not v or not v.strip():
            raise ValueError(f"用户名:{field}不能为空")
        length = len(v.strip())
        if length < 3:
            raise ValueError("用户名长度不能少于3个字符")
        if length > 20:
            raise ValueError("用户名长度不能超过20个字符")
        return v