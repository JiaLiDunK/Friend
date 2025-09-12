import asyncio
import logging
import os
import uuid
from typing import List

from src.friend.app.db.BooksDB import create_books_db
from src.friend.app.db.ChunkDB import create_chunk_db
from src.friend.entity.po.Books import Books
from src.friend.entity.po.Chunk import Chunk
from src.friend.utils.StringUtils import split_all_files_in_dir, load_chunk_document, clean_text


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
        logging.info("读取完成")


    async def read_and_save(self,paths: List[str]):
        # 防止并发复用
        books_db = await create_books_db()
        chunk_db = await create_chunk_db()
        for path in paths:
            try:
                sole_id = str(uuid.uuid4())
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
                logging.info(f"开始处理文件: {filename}, uuid={sole_id}")
                # 默认 type_id = 4
                type_id = 4
                # 如果 docs 太少，就改 type_id
                if not docs:
                    type_id = 5  # 你需要的 type_id 值
                elif len(docs) < 2:
                    type_id = 6
                book = Books(tittle=filename, uuid=sole_id, type_id=type_id)
                await books_db.insert_data(book)
                logging.info(f"插入 Book: {filename}")
                chunk_list: List[Chunk] = []
                i = 1
                for doc in docs:
                    safe_content = await clean_text(doc.page_content)
                    chunk = Chunk(content=safe_content, order_id=i, tittle_id=1, uuid=sole_id, type_id=2)
                    chunk_list.append(chunk)
                    i += 1
                await chunk_db.insert_list(chunk_list)
                logging.info(f"插入 {len(chunk_list)} 个 Chunks (文件: {filename})")
            except Exception as e:
                logging.error(f"处理文件失败: {path}, 错误: {e}", exc_info=True)