from typing import List

from fastapi import APIRouter, Depends
from loguru import logger

from src.friend.agents.node.ReadNode import ReadNode, get_read_node
from src.friend.entity.R import R
from src.friend.entity.vo.AddForm import AddBooks

readAndOutRouter = APIRouter()




@readAndOutRouter.post("/readBooks")
async def read_books(data:AddBooks,reading: ReadNode = Depends(get_read_node)):
    logger.info(f"导入书籍的信息:{data}")
    await reading.read_path(data)
    return R.ok().messages("测试中")


# 下述需要重构 或者删除
# @readAndOutRouter.post("/read")
# async def read_and_out(path: str,
#                        reading: ReadNode = Depends(get_read_node)):
#     """读取本机目录下的所有文件"""
#     logger.info(f"读取的路径{path}")
#     await reading.read_path(path)
#     return R.ok().messages("处理完成")
# 下述的方法暂时不知道是否可用
@readAndOutRouter.post("/repartition")
async def repartition(uuid_list:List[str],
                      reading: ReadNode = Depends(get_read_node)):
    """重新分割指定文件"""
    await reading.repartition_uuid(uuid_list)
    return R.ok().messages("重新切割成功")

@readAndOutRouter.post("/clearString")
async def clear_string(uuid_list:List[str],
                       text:str,
                       reading: ReadNode = Depends(get_read_node)):
    """清空指定文件指定的字符串"""
    await reading.clear_string(text, uuid_list)
    return R.ok().messages("清除完成")

@readAndOutRouter.post("/clearNewlineCharacter")
async def clear_newline_character(
        reading: ReadNode = Depends(get_read_node)):
    """清空所有的文件的换行符"""
    logger.info("清除多余的换行符")
    await reading.clear_newline_character_task()
    return "清除成功"

@readAndOutRouter.post("/repartitionAll")
async def repartition_all(reading: ReadNode = Depends(get_read_node)):
    """重新分割所有文件"""
    await reading.repartition_task()
    return "分割成功"

@readAndOutRouter.post("/clearStringAll")
async def clear_string_all(text:str,
        reading: ReadNode = Depends(get_read_node)):
    """清空所有文件指定的字符串"""
    await reading.clear_string_task(text)
    return "清除成功"