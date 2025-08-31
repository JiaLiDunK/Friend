from datetime import datetime

import sqlalchemy.dialects.postgresql as postgresql
from sqlmodel import SQLModel, Field, Column


class SysUser(SQLModel, table=True):
    __tablename__ = "sys_user"
    id: int = Field(
        sa_column=Column(postgresql.INTEGER,
                         primary_key=True,
                         unique=True,
                         autoincrement=True),
    )
    user_name: str
    password: str
    create_time: datetime
    salt: str
    email: str