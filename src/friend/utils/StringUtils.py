import asyncio
import random
import string
import re
import os
from typing import List
from langchain_community.document_loaders import PyPDFLoader, TextLoader, UnstructuredWordDocumentLoader
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


async def load_chunk_document(path: str, chunk_size: int, chunk_overlap: int, separators: List[str]):
    """根据文件后缀名加载并切割文档"""
    ext = os.path.splitext(path)[1].lower()  # 获取后缀名
    # 根据文件类型选择 loader
    if ext == ".pdf":
        loader = PyPDFLoader(path)
    elif ext in [".doc", ".docx"]:
        loader = UnstructuredWordDocumentLoader(path)
    elif ext in [".txt", ".md"]:
        loader = TextLoader(path, encoding="utf-8")
    else:
        raise ValueError(f"暂不支持的文件类型: {ext}")
    # 加载文档
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
async def split_all_files_in_dir(dir_path: str, parts: int = 10) -> List[List[str]]:
    """
    遍历目录，把文件路径均分到 parts 份
    :param dir_path: 目录路径
    :param parts: 需要切分的份数
    :return: 二维列表，每个子列表是一份文件路径
    """
    # 收集所有文件
    all_files = []
    for root, dirs, files in os.walk(dir_path):
        for file in files:
            file_path = os.path.join(root, file)
            all_files.append(file_path)
    if not all_files:
        return [[] for _ in range(parts)]  # 没有文件时，返回空份
    # 计算每份大概的数量
    n = len(all_files)
    result: List[List[str]] = [[] for _ in range(parts)]
    # 均匀分配文件
    for i, file_path in enumerate(all_files):
        result[i % parts].append(file_path)
    return result