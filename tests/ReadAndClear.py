import asyncio
import os
import uuid
from typing import List

from src.friend.entity.po.Books import Books
from src.friend.entity.po.Chunk import Chunk
from src.friend.utils import StringUtils
from src.friend.utils.StringUtils import load_chunk_document


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

async def read_and_save(paths:List[str]):
    for path in paths:
        sole_id = uuid.uuid4()
        docs = await load_chunk_document(path,
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
        book = Books(tittle=filename,uuid=sole_id,type_id=0)
        chunk_list:List[Chunk] = []
        i = 1
        for doc in docs:
            chunk = Chunk(content=doc.page_content,order_id=i,tittle_id=1,uuid=sole_id,type_id=2)
            chunk_list.append(chunk)
async def task(name, sec):
    print(f"开始任务 {name}")
    await asyncio.sleep(sec)
    print(f"完成任务 {name}")
    return f"结果-{name}"


async def main():
    directory = r"" # 换成你的目录
    docs = await StringUtils.load_chunk_document(directory,chunk_size=612,
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
    for doc in docs:
        pass


if __name__ == "__main__":
    # book_path = r"D:\测试资料\book\pua\魔鬼约会学 - 魔鬼咨询师.epub"
    # # 载入电子书
    # book = epub.read_epub(book_path)
    # # 解析
    # # spine 里是章节的顺序
    # for item_id, _ in book.spine:
    #     item = book.get_item_with_id(item_id)
    #     if item and item.get_type() == ebooklib.ITEM_DOCUMENT:  # 注意这里
    #         soup = BeautifulSoup(item.get_content(), "html.parser")
    #         print(soup.get_text())  # 打印前 200 字
    asyncio.run(main())

    # arr = split_all_files_in_dir(directory)
    # arr_all = []
    # for i in arr:
    #     for j in i:
    #         arr_all.append(j)
    # asyncio.run(read_and_save(arr_all))
