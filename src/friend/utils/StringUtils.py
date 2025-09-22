import asyncio
from loguru import logger
import os
import random
import re
import string
from typing import List, Any
import ebooklib
import pdfplumber
from bs4 import BeautifulSoup
from ebooklib import epub
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader, UnstructuredWordDocumentLoader
from pdfplumber.utils.exceptions import PdfminerException


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


async def load_chunk_document(path: str, chunk_size: int, chunk_overlap: int, separators: list):
    """根据文件后缀名加载并切割文档"""
    ext = os.path.splitext(path)[1].lower()  # 获取后缀名
    if ext == ".pdf":
        # 尝试用 pdfplumber 提取文本
        text = await extract_text_pdf_safe(path)
        documents = [Document(page_content=text)]
    elif ext in [".doc", ".docx"]:
        loader = UnstructuredWordDocumentLoader(path)
        documents = loader.load()
    elif ext in [".txt", ".md"]:
        loader = TextLoader(path, encoding="utf-8")
        documents = loader.load()
    elif ext == ".epub":
        book = epub.read_epub(path)
        documents = []
        # 解析
        for item in book.get_items():
            if item.get_type() == ebooklib.ITEM_DOCUMENT:
                soup = BeautifulSoup(item.get_content(), "html.parser")
                text = soup.get_text().strip()
                if text:
                    documents.append(Document(page_content=text))
    else:
        logger.info(f"暂时无法处理文件:{ext}")
        documents = []
    # 定义切割器
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=separators
    )
    # 切割文档
    docs = text_splitter.split_documents(documents)
    return docs

async def extract_text_pdf_safe(path: str) -> str:
    """
    安全提取 PDF 文本：
    - 优先使用 pdfplumber 提取
    - 若报错或异常字体，使用 OCR 提取
    """
    text = ""
    try:
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                try:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                except PdfminerException:
                    # 当前页字体异常，跳过
                    continue
        # 如果 pdfplumber 提取为空，走 OCR ,主动放弃
        if not text.strip():
            text = ""
    except Exception:
        # pdfplumber 打开失败，走 OCR,主动放弃
        text = ""
    return text

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
async def clean_text(text: str) -> str:
    """
    清理掉 PostgreSQL UTF8 不允许的字符:
    - NULL (\x00)
    - 非法 surrogate 字符 (\ud800-\udfff)
    - 其他控制字符 (0x01–0x1F, 0x7F)，但保留 \n 和 \t
    """
    if not isinstance(text, str):
        return text
    # 去掉 NULL
    text = text.replace("\x00", "")
    # 去掉 surrogate 范围
    text = re.sub(r"[\ud800-\udfff]", "", text)
    # 去掉不可见控制符 (除了 \n \t)
    text = re.sub(r"[\x01-\x08\x0B-\x0C\x0E-\x1F\x7F]", "", text)
    # 去掉多余空白
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()

async def compress_newlines(texts: str, keep: int = 1, strip_indent: bool = True) -> str:
    """
    将多个连续的空白行压缩为指定数量的换行。
    默认压缩为 1 个 \n，并清理开头和结尾的多余空白行。

    :param texts: 源字符串
    :param keep: 保留多少个换行符
    :param strip_indent: 是否去掉每行前面的缩进空格
    """
    texts = re.sub(r'[\u200B-\u200D\uFEFF]', '', texts)
    # 统一换行符
    texts = texts.replace("\r\n", "\n").replace("\r", "\n")
    # 压缩多个空白行
    texts = re.sub(r'[ \t]*\n[ \t]*(\n[ \t]*)+', "\n" * keep, texts)
    # 去掉开头和结尾的空白行
    texts = texts.strip("\n \t")
    if strip_indent:
        # 去掉每行行首的空格和制表符
        texts = re.sub(r'^[ \t]+', '', texts, flags=re.MULTILINE)
    return texts

async def remove_substring(text: str, target: str) -> str:
    """
    目前先这样吧,后续可能需要更新
    删除字符串中指定的子串（精确匹配）
    """
    return text.replace(target, "")
async def chunk_array(arr: List[Any], size: int = 10) -> List[List[Any]]:
    """
    将数组均分成指定大小的二维数组（最后一组可能不足 size 个）
    :param arr: 原始一维数组
    :param size: 每组的最大元素个数，默认 10
    :return: 分块后的二维数组
    """
    return [arr[i:i + size] for i in range(0, len(arr), size)]

async def chunk_docs(all_text:str):
    """重写切割用的方法"""
    # 定义切割器
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=612,
        chunk_overlap=100,
        separators=[
        "\n\n",  # 段落
        "\n",  # 单换行
        "。", "！", "？", "；",  # 中文句号/感叹号/问号/分号
        ".", "!", "?", ";",  # 英文句号/感叹号/问号/分号
        "，", ",",  # 中文、英文逗号
        "：", ":",  # 中文、英文冒号
        " ",  # 空格
        ""  # 最后兜底（强制切割）
]
    )
    # 切割文档
    docs = text_splitter.split_text(all_text)
    return docs