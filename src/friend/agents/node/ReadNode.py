import asyncio
import os
import uuid
from typing import List

from loguru import logger
from src.friend.app.db.BooksDB import create_books_db
from src.friend.app.db.ChunkDB import create_chunk_db
from src.friend.entity.po.Books import Books
from src.friend.entity.po.Chunk import Chunk
from src.friend.utils.StringUtils import split_all_files_in_dir, load_chunk_document, clean_text, remove_substring, \
    chunk_docs, chunk_array, compress_newlines


class ReadNode:
    def __init__(self,books_db,chunk_db):
        self.books_db = books_db
        self.chunk_db = chunk_db
    @classmethod
    async def create(cls):
        books_db = await create_books_db()
        chunk_db = await create_chunk_db()
        return cls(books_db, chunk_db)
    async  def clear_string_task(self,text:str):
        """清除所有文件中的指定内容"""
        logger.info("开始清除")
        data_list = await self.chunk_db.select_all_uuid()
        task_list = await chunk_array(data_list)
        tasks = [asyncio.create_task(self.clear_string(text,task)) for task in task_list]
        # 等待任务完成
        await asyncio.gather(*tasks)
        logger.info("清除完成")
    async def clear_string(self,text:str,uuid_list:List[str]):
        """清除指定uuid中的指定内容"""
        chunk_db = await create_chunk_db()
        for uuids in uuid_list:
           chunk_list = await self.chunk_db.get_data_uuid(uuids)
           for chunk in chunk_list:
               chunk.content = await remove_substring(chunk.content, text)
           await chunk_db.update_data_list(chunk_list)
    async def repartition_task(self):
        """重新分割所有文件中的内容"""
        logger.info("开始重新分割")
        data_list = await self.chunk_db.select_all_uuid()
        task_list = await chunk_array(data_list)
        tasks = [asyncio.create_task(self.repartition_uuid(task)) for task in task_list]
        # 等待任务完成
        await asyncio.gather(*tasks)
        logger.info("重新分割完成")
    async def repartition_uuid(self,uuid_list:List[str]):
        """重新分割指定uuid文档中的内容"""
        for uuids in uuid_list:
            chunk_list = await self.chunk_db.get_data_uuid(uuids)
            all_docs = ""
            for chunk in chunk_list:
                all_docs += chunk.content
            docs = await chunk_docs(all_docs)
            chunk_list: List[Chunk] = []
            i = 1
            for doc in docs:
                chunk = Chunk(content=doc.page_content, order_id=i, title_id=1, uuid=uuids, type_id=2)
                chunk_list.append(chunk)
                i += 1
            await self.chunk_db.update_data_list(chunk_list)

    async def read_path(self,path:str):
        """多线程启动的---分割指定目录下的文本文件"""
        arr = await split_all_files_in_dir(path)
        tasks = [asyncio.create_task(self.read_and_save(paths)) for paths in arr]
        # 等待任务完成
        await asyncio.gather(*tasks)
        logger.info("读取完成")

    async def read_and_save(self,paths: List[str]):
        """分割保存指定目录下的文本文件"""
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
                logger.info(f"开始处理文件: {filename}, uuid={sole_id}")
                # 默认 type_id = 4
                type_id = 4
                # 如果 docs 太少，就改 type_id
                if not docs:
                    type_id = 5  # 你需要的 type_id 值
                elif len(docs) < 2:
                    type_id = 6
                book = Books(tittle=filename, uuid=sole_id, type_id=type_id)
                await books_db.insert_data(book)
                logger.info(f"插入 Book: {filename}")
                chunk_list: List[Chunk] = []
                i = 1
                for doc in docs:
                    safe_content = await clean_text(doc.page_content)
                    chunk = Chunk(content=safe_content, order_id=i, tittle_id=1, uuid=sole_id, type_id=2)
                    chunk_list.append(chunk)
                    i += 1
                await chunk_db.insert_list(chunk_list)
                logger.info(f"插入 {len(chunk_list)} 个 Chunks (文件: {filename})")
            except Exception as e:
                logger.error(f"处理文件失败: {path}, 错误: {e}", exc_info=True)
    async def clear_newline_character_task(self):
        """多线程启动的方法-把所有的内容中的多个\n变成一个"""
        logger.info("任务启动")
        data_list = await self.chunk_db.select_all_uuid()
        task_list = await chunk_array(data_list)
        tasks = [asyncio.create_task(self.clear_newline_character(task)) for task in task_list]
        # 等待任务完成
        await asyncio.gather(*tasks)
        logger.info("任务完成")
    async def clear_newline_character(self,uuid_list:List[str]):
        """把所有的内容中的多个\n变成一个"""
        # 防止并发复用
        chunk_db = await create_chunk_db()
        chunk_list:List[Chunk] = []
        for uuids in uuid_list:
            chunk_list = await chunk_db.get_data_uuid(uuids)
            for chunk in chunk_list:
                chunk.content = await compress_newlines(chunk.content)
        await chunk_db.update_data_list(chunk_list)

