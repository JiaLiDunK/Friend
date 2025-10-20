from typing import List

from fastapi import APIRouter, Depends
from loguru import logger
from src.friend.app.db.BookVectorsDB import create_book_vectors_db, BookVectorsDB
from src.friend.app.db.BooksDB import BooksDB, create_books_db
from src.friend.app.db.ChunkDB import ChunkDB, create_chunk_db
from src.friend.entity.R import R
from src.friend.entity.po.BookVectors import BookVectors
from src.friend.entity.po.Books import Books
from src.friend.entity.po.Chunk import Chunk
from src.friend.entity.vo.QueryTable import QueryTable

booksRouter = APIRouter()


@booksRouter.post("/getBookList")
async def get_book_list(
        data:QueryTable,
        books_db:BooksDB=Depends(create_books_db))->R:
    """获取书籍的列表"""
    logger.info(f"查询书籍的信息:{data}")
    result = await books_db.get_data_list(data)
    return R.ok().messages("查询成功").data_dict(result)

@booksRouter.post("/updateBook")
async def update_book(data:Books,books_db:BooksDB=Depends(create_books_db))->R:
    """更新书籍的信息"""
    logger.info(f"更新书籍的信息:{data}")
    await books_db.update_data(data)
    return R.ok().messages("更新成功")

@booksRouter.post("/getChunkList")
async def get_chunk_list(data:QueryTable,chunk_db:ChunkDB=Depends(create_chunk_db)) -> R:
    """获取书籍的分片"""
    logger.info(f"查询书籍的分片:{data}")
    result = await chunk_db.get_data_list(data)
    return R.ok().messages("查询成功").data_dict(result)

@booksRouter.post("/updateChunkList")
async def update_chunk(data_list:List[Chunk],chunk_db:ChunkDB=Depends(create_chunk_db))->R:
    """更新书籍的分片"""
    logger.info(f"更新书籍的分片:{data_list}")
    for data in data_list:
        await chunk_db.update_data(data)
    return R.ok().messages("更新成功")

@booksRouter.post("/putBookVectors")
async def put_book_vectors(data:Books,book_vectors_db:BookVectorsDB=Depends(create_book_vectors_db),
                           book_db:BooksDB=Depends(create_books_db))->R:
    """把书籍进行向量化"""
    logger.info(f"书籍向量化{data}")
    book_data = BookVectors(uuid=data.uuid,type_id=8,knowledge_base_id=0)
    await book_vectors_db.insert_data(book_data)
    data.type_id = 9
    await book_db.update_data(data)
    return R.ok().messages("已推送")

@booksRouter.post("/getList")
async def get_list(data:QueryTable,book_vectors_db:BookVectorsDB=Depends(create_book_vectors_db))->R:
    """获取准备书籍的向量"""
    logger.info(f"查询书籍的向量:{data}")
    result = await book_vectors_db.get_data_list(data)
    return R.ok().messages("查询成功").data_dict(result)

@booksRouter.post("/updateBooksVectors")
async def update_books_vectors(data:BookVectors,book_vectors_db:BookVectorsDB=Depends(create_book_vectors_db))->R:
    """更新准备向量的书籍"""
    logger.info(f"更新准备向量的书籍:{data}")
    await book_vectors_db.update_data(data)
    return R.ok().messages("更新成功")

@booksRouter.post("/delBooksVectors")
async def del_book_vectors(data:BookVectors,book_vectors_db:BookVectorsDB=Depends(create_book_vectors_db))->R:
    """删除数据"""
    logger.info(f"删除数据:{data}")
    await book_vectors_db.del_data(data)
    return R.ok().messages("删除成功")