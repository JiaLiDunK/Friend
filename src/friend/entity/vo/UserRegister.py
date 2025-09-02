from pydantic import BaseModel, field_validator


class UserRegister(BaseModel):
    """用户注册"""
    username: str
    password: str
    confirmPassword: str
    @field_validator('username','password','confirmPassword')
    def check_user_name(cls, v, field):
        if not v or not v.strip():
            raise ValueError(f"用户名:{field}不能为空")
        length = len(v.strip())
        if length < 3:
            raise ValueError("用户名长度不能少于3个字符")
        if length > 20:
            raise ValueError("用户名长度不能超过20个字符")
        return v