from dataclasses import dataclass, field, is_dataclass, asdict
from typing import Any, Mapping

from pydantic import BaseModel


@dataclass
class R:
    success: bool = None
    message: str = None
    code: int = None
    # 允许任意数据类型，便于直接塞入 Pydantic 模型或原生对象
    data: Any = field(default_factory=dict)
    jwt: str = None

    @classmethod
    def ok(cls):
        return cls(success=True, code=200)

    @classmethod
    def error(cls):
        return cls(success=False, code=500)

    def bool_success(self, success: bool):
        self.success = success
        return self

    def messages(self, msg: str):
        self.message = msg
        return self

    def code_value(self, code: int):
        self.code = code
        return self

    def data_item(self, key: str, value: Any):
        # 确保 data 可作为字典使用
        if not isinstance(self.data, dict):
            self.data = {}
        self.data[key] = value
        return self

    def data_dict(self, data: Any):
        # 兼容多种数据类型，自动转换为可序列化的字典
        if isinstance(data, BaseModel):
            self.data = data.model_dump()
        elif hasattr(data, "model_dump") and callable(getattr(data, "model_dump")):
            # 兼容可能的自定义 Pydantic 模型
            self.data = data.model_dump()
        elif is_dataclass(data):
            self.data = asdict(data)
        elif isinstance(data, Mapping):
            self.data = dict(data)
        else:
            # 直接赋值，交由 FastAPI/Pydantic 处理（一般为基础类型或已可序列化对象）
            self.data = data
        return self

    def jwt_value(self, jwt: str):
        self.jwt = jwt
        return self
