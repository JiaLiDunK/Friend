import asyncio
import base64
import os
import random
import re
import string
from io import BytesIO
from typing import List, Any

import ebooklib
import fitz
import pdfplumber
from PIL import Image
from bs4 import BeautifulSoup
from ebooklib import epub
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.chat_models import ChatTongyi
from langchain_community.document_loaders import TextLoader, UnstructuredWordDocumentLoader
from langchain_core.messages import HumanMessage
from langchain_ollama import ChatOllama
from loguru import logger
from pdfplumber.utils.exceptions import PdfminerException

from src.friend.config.SettingConfig import settings


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
        if not text.strip() or len(text.strip())<=1000:
            text = await ocr_text(path)
    except Exception:
        # pdfplumber 打开失败，走 OCR,主动放弃
        text = await ocr_text(path)
    return text

async def pdf_to_images(pdf_path):
    """
    将PDF文件转换为图片列表

    Args:
        pdf_path (str): PDF文件路径

    Returns:
        list: 包含每页图片的列表
    """
    images = []
    pdf_document = fitz.open(pdf_path)

    for page_num in range(len(pdf_document)):
        page = pdf_document[page_num]
        # 设置较高的缩放因子以提高图像质量
        mat = fitz.Matrix(2.0, 2.0)
        pix = page.get_pixmap(matrix=mat)

        # 转换为PIL Image
        img_data = pix.tobytes("ppm")
        img = Image.open(BytesIO(img_data))
        # 确保图片是RGB模式
        if img.mode != 'RGB':
            img = img.convert('RGB')
        images.append(img)

    pdf_document.close()
    return images

async def image_to_base64(image):
    """
    将PIL Image转换为base64编码

    Args:
        image (PIL.Image): 图片对象

    Returns:
        str: base64编码的图片数据
    """
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return img_str
async def ocr_with_qwen_vl_langchain(image, prompt="请识别图片中的文字内容，只返回图片中文字的内容，去掉多余的空格或换行符，如果没有文字则返回空字符串"):
    """
    使用LangChain调用通义 Qwen-VL-OCR 模型进行OCR识别
    Args:
        image (PIL.Image): 要识别的图片
        prompt (str): 提示词
    Returns:
        str: 识别的文字内容
    """
    # 将图片转换为 base64
    img_base64 = await image_to_base64(image)

    # 初始化通义多模态模型
    llm = ChatTongyi(
        model="qwen-vl-ocr",
        api_key=settings.API_KEY_ALI,
        model_kwargs={"temperature": 0.3}
    )

    # 构造消息（多模态内容）
    message = HumanMessage(
        content=[
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": f"data:image/png;base64,{img_base64}"}
        ]
    )

    try:
        # 调用模型（异步）
        response = await llm.ainvoke([message])
        return response.content
    except Exception as e:
        print(f"请求异常: {e}")
        return ""
async def ocr_with_qwen_vl_langchain_ollama(image, prompt="请识别图片中的文字内容,只返回图片中文字的内容,去掉多余的空格或者换行符,如果没有可返回的文字内容，直接返回一个空字符串"""):
    """
    使用LangChain调用本地Qwen2.5-VL模型进行OCR识别

    Args:
        image (PIL.Image): 要识别的图片
        prompt (str): 提示词

    Returns:
        str: 识别的文字内容
    """
    # 将图片转换为base64
    img_base64 = await image_to_base64(image)

    # 初始化ChatOllama模型（支持视觉模型）
    llm = ChatOllama(model="qwen2.5vl:7b")

    # 构造消息内容
    message = HumanMessage(
        content=[
            {"type": "text", "text": prompt},
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/png;base64,{img_base64}"
                }
            },
        ]
    )

    try:
        # 调用模型
        response = await llm.ainvoke([message])
        return response.content
    except Exception as e:
        print(f"请求异常: {e}")
        return ""
async def ocr_text(path: str) -> str:
    """OCR识别整本PDF并返回完整字符串，使用LLM视觉模型进行OCR识别"""
    logger.info(f"进入了OCR识别中")
    all_text = ""

    try:
        pdf_document = fitz.open(path)
        total_pages = len(pdf_document)

        for page_number in range(total_pages):
            try:
                page = pdf_document[page_number]
                # 提高渲染分辨率
                zoom = 2.0
                mat = fitz.Matrix(zoom, zoom)
                pix = page.get_pixmap(matrix=mat)

                # 转换为PIL Image
                img_data = pix.tobytes("ppm")
                image = Image.open(BytesIO(img_data))
                # 确保图片是RGB模式
                if image.mode != 'RGB':
                    image = image.convert('RGB')
                # 使用LLM视觉模型进行OCR识别
                page_text = await ocr_with_qwen_vl_langchain(
                    image,
                    "请识别图片中的文字内容，只返回图片中文字的内容，去掉多余的空格或者换行符，如果没有可返回的文字内容，直接返回一个空字符串"
                )
                all_text += page_text
                # 给事件循环一个机会（避免长时间阻塞）
                await asyncio.sleep(0)
                logger.info(f"识别完{page_number}")
                logger.info(f"识别结果:\n {page_text}")
            except Exception as e:
                logger.error(f"处理第{page_number}页时出错: {e}")
                continue
    except Exception as e:
        logger.error(f"打开PDF文件失败: {e}")
        raise
    finally:
        # 确保资源释放
        if 'pdf_document' in locals():
            pdf_document.close()
    return all_text


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
        "。", "！", "？", "；",  # 中文句号/感叹号/问号/分号
        ".", "!", "?", ";",  # 英文句号/感叹号/问号/分号
        "\n\n",  # 段落
        "，", ",",  # 中文、英文逗号
        "：", ":",  # 中文、英文冒号
        "\n",  # 单换行
        " ",  # 空格
        ""  # 最后兜底（强制切割）
]
    )
    # 切割文档
    docs = text_splitter.split_text(all_text)
    return docs