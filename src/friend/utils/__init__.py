import time

import jwt

from src.friend.config.SettingConfig import settings



data = {
    "email":"333",
    "pwd":"hhh"
}
to_encode = data.copy()
to_encode.update({"exp":time.time()+settings.ACCESS_TOKEN_EXPIRE_MINUTES})
encode_jwt = jwt.encode(to_encode,settings.SECRET_KEY,algorithm=settings.ALGORITHM)
print(encode_jwt)
res = jwt.decode(encode_jwt,settings.SECRET_KEY,algorithms=[settings.ALGORITHM])
print(res)