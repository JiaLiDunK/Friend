import asyncio
import random
import string
import re
from typing import List


async def generate_random_string(length=8):
    """生成随机字符串"""
    characters = string.ascii_letters + string.digits  # 字母+数字
    return ''.join(random.choice(characters) for _ in range(length))

async def remove_whitespace(text:str)->str:
    return re.sub(r'\s+','',text)

async def remove_whitespace_list(text: List[str]) -> List[str]:
    return await asyncio.gather(*(remove_whitespace(t) for t in text))
