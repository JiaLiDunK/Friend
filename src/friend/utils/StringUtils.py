import asyncio
import random
import string
import re
from typing import List
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

async def generate_random_string(length=8):
    """生成随机字符串"""
    characters = string.ascii_letters + string.digits  # 字母+数字
    return ''.join(random.choice(characters) for _ in range(length))

async def remove_whitespace(text:str)->str:
    """删除字符串中的空白字符"""
    return re.sub(r'\s+','',text)

async def remove_whitespace_list(text: List[str]) -> List[str]:
    """删除列表中每个字符串的空白字符"""
    return await asyncio.gather(*(remove_whitespace(t) for t in text))


async def load_chunk_document_pdf(path:str,chunk_size:int,chunk_overlap:int,separators:List[str]):
    """加载切割文档"""
    loader = PyPDFLoader(path)
    documents = loader.load()
    # 定义切割器
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=separators
    )
    # 切割文档
    docs = text_splitter.split_documents(documents)
    return docs