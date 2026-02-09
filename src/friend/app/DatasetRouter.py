import uuid
from datetime import datetime

from fastapi import APIRouter, Depends
from loguru import logger

from src.friend.agents.node.ChatNode import ChatNode, get_chat_node
from src.friend.agents.node.ReadNode import ReadNode, get_read_node
from src.friend.app.db.DatasetDB import DatasetDB, create_dataset_db
from src.friend.app.db.JoinLinkDB import JoinLinkDB, create_join_link_db
from src.friend.entity.R import R
from src.friend.entity.po.dataset import Dataset
from src.friend.entity.vo.QueryTable import QueryTable

datasetRouter = APIRouter()

@datasetRouter.post("/getList")
async def get_list(data:QueryTable,dataset_db:DatasetDB=Depends(create_dataset_db)):
    logger.info(f"查询数据:{data}")
    result = await dataset_db.get_data_list(data)
    return R.ok().data_dict(result)
@datasetRouter.post("/add")
async def add(data:Dataset,dataset_db:DatasetDB=Depends(create_dataset_db)):
    logger.info(f"添加数据:{data}")
    data.sole_uuid = str(uuid.uuid4())
    data.create_time = datetime.now()
    result = await dataset_db.insert_data(data)
    return R.ok().messages(result)
@datasetRouter.post("/delData")
async def del_data(data:Dataset,dataset_db:DatasetDB=Depends(create_dataset_db)):
    logger.info(f"删除数据:{data}")
    result = await dataset_db.del_data(data)
    return R.ok().messages(result)
@datasetRouter.post("/update")
async def update(data:Dataset,dataset_db:DatasetDB=Depends(create_dataset_db)):
    logger.info(f"更新数据:{data}")
    result = await dataset_db.update_data(data)
    return R.ok().messages(result)
@datasetRouter.post("/scoring")
async def scoring(data:Dataset,join_link_db:JoinLinkDB=Depends(create_join_link_db),
                  read: ReadNode = Depends(get_read_node)):
    logger.info(f"给数据集中所有的数据打分:{data}")
    result = await join_link_db.get_books_data_by_scoring(data.id)
    await read.create_scoring_by_dataset(result)
    return R.ok().messages("完成")

@datasetRouter.post("/extract")
async def extract(data:Dataset,join_link_db:JoinLinkDB=Depends(create_join_link_db),
                  read: ReadNode = Depends(get_read_node)):
    logger.info(f"从数据集中所有的数据提取数据:{data}")
    result = await join_link_db.get_books_data_by_extract(data.id)
    await read.create_extract_by_dataset(result)
    return R.ok().messages("完成")

@datasetRouter.post("/getOptions")
async def get_options(dataset_db:DatasetDB=Depends(create_dataset_db)):
    logger.info("获取选项")
    result = await dataset_db.get_options()
    return R.ok().data_dict(result)

@datasetRouter.post("/clearChunk")
async def clear_chunk(data:Dataset,read: ReadNode = Depends(get_read_node),
                      chat_node:ChatNode=Depends(get_chat_node)):
    logger.info(f"清理一下指定文本的chunk:\n{data}")
    # result = await join_link_db.get_books_data_by_extract(data.id)
    # await chat_node.user_ollama_qwen3_abliterated_8b_7("你好啊")
    message = "26.5.3　编写脚本edit.cgi\n脚本edit.cgi实际上承担了双重职责：既用于编辑新消息，也用于编辑回复。这两项功能的差别并不大：如果在CGI请求中提供了reply_to，就将其存储在编辑表单中一个隐藏的input元素中。在Web表单中，隐藏的input元素用于临时存储信息。它们不像文本区域等元素那样是用户能够看到的，但它们的值也将传递给表单的属性action指定的CGI脚本，这让生成表单的脚本能够向处理该表单的脚本传递信息。\n另外，默认将主题设置为\"Re: parentsubject\"（除非主题已经以Re:打头，在这种情况下，不用继续添加Re:）。处理这些细节的代码片段如下：\nsubject = ''\nif reply_to is not None:\n print('<input type=\"hidden\" name=\"reply_to\" value=\"{}\"/>'.format(reply_to))\n curs.execute('SELECT subject FROM messages WHERE id = %s', (reply_to,))\n subject = curs.fetchone()[0]\n if not subject.startswith('Re: '):\n subject = 'Re: ' + subject"
    res = await read.clear_chunk(message)
    for item in res:
        print(item)
    return R.ok().messages("完成")