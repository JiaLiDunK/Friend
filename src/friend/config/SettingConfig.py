from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()

# 设置 配置字典
class Settings(BaseSettings):
    DATABASE_MYSQL_URL: str = Field(default="未定义")
    DATABASE_PG_URL: str = Field(default="未定义")
    HOST: str = Field(default="127.0.0.1")
    PORT: int = Field(default=8091)
    SECRET_KEY: str | None = None
    ALGORITHM:str = Field(default='HS256')
    ACCESS_TOKEN_EXPIRE_MINUTES:int = Field(default=30)
    BASE_URL_ALI: str | None = None
    CODE_MODEL: str | None = None
    API_KEY_ALI: str | None = None
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )
settings = Settings()
