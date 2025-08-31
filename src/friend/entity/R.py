from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass
class R:
    success: bool = None
    message: str = None
    code: int = None
    data: Dict[str, Any] = field(default_factory=dict)
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
        self.data[key] = value
        return self

    def data_dict(self, data: Dict[str, Any]):
        self.data = data
        return self

    def jwt_value(self, jwt: str):
        self.jwt = jwt
        return self
