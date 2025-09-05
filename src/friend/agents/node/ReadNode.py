import asyncio
import os
import uuid
from typing import List


from src.friend.app.db.BooksDB import create_books_db
from src.friend.app.db.ChunkDB import create_chunk_db
from src.friend.entity.po.Books import Books
from src.friend.entity.po.Chunk import Chunk
from src.friend.utils.StringUtils import split_all_files_in_dir, load_chunk_document


class ReadNode:
    def __init__(self,books_db,chunk_db):
        self.books_db = books_db
        self.chunk_db = chunk_db
    @classmethod
    async def create(cls):
        books_db = await create_books_db()
        chunk_db = await create_chunk_db()
        return cls(books_db, chunk_db)

    async def read_path(self,path:str):
        """分割指定目录下的文本文件"""
        arr = await split_all_files_in_dir(path)
        tasks = [asyncio.create_task(self.read_and_save(paths)) for paths in arr]
        # 等待任务完成
        await asyncio.gather(*tasks)


    async def read_and_save(self,paths: List[str]):
        # 防止并发复用
        books_db = await create_books_db()
        chunk_db = await create_chunk_db()
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
            book = Books(title=filename, uuid=sole_id, type_id=0)
            await books_db.insert_data(book)
            chunk_list: List[Chunk] = []
            i = 1
            for doc in docs:
                chunk = Chunk(content=doc.page_content, order_id=i, title_id=1, uuid=sole_id, type_id=2)
                chunk_list.append(chunk)
            await chunk_db.insert_list(chunk_list)