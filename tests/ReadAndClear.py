import uuid
from typing import List

from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os
import asyncio

from openpyxl.styles.builtins import title
from sympy import content

from friend.entity.po.Books import Books
from friend.entity.po.Chunk import Chunk
from friend.utils.StringUtils import load_chunk_document_pdf

def split_all_files_in_dir(dir_path, parts=10):
    """遍历目录，把文件均分到 parts 份"""
    # 收集所有文件
    all_files = []
    for root, dirs, files in os.walk(dir_path):
        for file in files:
            file_path = os.path.join(root, file)
            all_files.append(file_path)

    # 初始化二维数组，长度为 parts（例如 10）
    # 每个元素是一个空列表，用来存放一组文件
    arr = [[] for _ in range(parts)]

    # 遍历所有文件，同时获取它们的索引 idx
    for idx, file in enumerate(all_files):
        # idx % parts 的作用是取余数
        # 这样文件会“轮流”放到 arr[0], arr[1], arr[2] ... arr[parts-1]
        # 当 idx 达到 parts 后，又会从 arr[0] 开始放
        # 结果就是把文件均匀分配到每一组
        arr[idx % parts].append(file)

    return arr
async def task(name, sec):
    print(f"开始任务 {name}")
    await asyncio.sleep(sec)
    print(f"完成任务 {name}")
    return f"结果-{name}"
async def read_and_save(paths:List[str]):
    for path in paths:
        sole_id = uuid.uuid4()
        print(sole_id)
        docs = await load_chunk_document_pdf(path,
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
])
        filename = os.path.basename(path)
        book = Books(title=filename,uuid=sole_id,type_id=0)
        chunk_list = List[Chunk]
        i = 1
        # for doc in docs:
        #     chunk = Chunk(content=doc.page_content,order_id=i,title_id=1,uuid=sole_id,type_id=2)
        #     chunk_list.append(chunk)
        print(book)


async def read_one(path:str):
    docs = await load_chunk_document_pdf(path,
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
                                         ])
    filename = os.path.basename(path)
    book = Books(title=filename, uuid="6789098765", type_id=0)
    chunk_list:List[Chunk] = []
    i = 1
    for doc in docs:
        chunk = Chunk(content=doc.page_content,order_id=i,title_id=1,uuid="4567890",type_id=2)
        print(doc.page_content)
        print("================")
        chunk_list.append(chunk)
    print(chunk_list)



async def main():
    # 并发执行多个任务
    tasks = [asyncio.create_task(task(f"T{i}", i)) for i in range(1, 6)]

    # 等待所有任务完成
    results = await asyncio.gather(*tasks)
    print("所有结果:", results)



if __name__ == "__main__":
    directory = r"D:\资料\pdf\【华为】Java岗面试真题.pdf"  # 换成你的目录
    # arr = split_all_files_in_dir(directory)
    # asyncio.run(read_and_save(arr[1]))
    asyncio.run(read_one(directory))
