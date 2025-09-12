import logging
from typing import List

from fastapi import APIRouter, Depends

from src.friend.app.db.BooksDB import BooksDB, create_books_db
from src.friend.app.db.ChunkDB import ChunkDB, create_chunk_db
from src.friend.entity.R import R
from src.friend.entity.po.Books import Books
from src.friend.entity.po.Chunk import Chunk
from src.friend.entity.vo.QueryTable import QueryTable

booksRouter = APIRouter()


@booksRouter.post("/getBookList")
async def get_book_list(
        data:QueryTable,
        books_db:BooksDB=Depends(create_books_db))->R:
    """获取书籍的列表"""
    logging.info(f"查询书籍的信息:{data}")
    result = await books_db.get_data_list(data)
    return R.ok().messages("查询成功").data_dict(result)

@booksRouter.post("/updateBook")
async def update_book(data:Books,books_db:BooksDB=Depends(create_books_db))->R:
    """更新书籍的信息"""
    logging.info(f"更新书籍的信息:{data}")
    await books_db.update_data(data)
    return R.ok().messages("更新成功")

@booksRouter.post("/getChunkList")
async def get_chunk_list(data:QueryTable,chunk_db:ChunkDB=Depends(create_chunk_db)) -> R:
    """获取书籍的分片"""
    logging.info(f"查询书籍的分片:{data}")
    result = await chunk_db.get_data_list(data)
    return R.ok().messages("查询成功").data_dict(result)

@booksRouter.post("/updateChunkList")
async def update_chunk(data_list:List[Chunk],chunk_db:ChunkDB=Depends(create_chunk_db))->R:
    """更新书籍的分片"""
    logging.info(f"更新书籍的分片:{data_list}")
    for data in data_list:
        await chunk_db.update_data(data)
    return R.ok().messages("更新成功")
