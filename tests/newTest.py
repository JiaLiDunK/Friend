from typing import List

import pytest
import asyncio


from friend.agents.node.RagNode import RagNode
from src.friend.agents.node.MilvusNode import MilvusNode
from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.friend.utils.StringUtils import remove_whitespace_list


# 连接到 Milvus 服务（默认端口是 19530）



async def async_to_embedding():
    node = RagNode()
    list_text: List[str] = ["这是一个测试的文本1", "这是一个测试文本2"]
    embeddings = await node.text_to_embedding_documents_bge(list_text)
    print("开始输出")
    print(len(embeddings[0]))
    print(embeddings[1])

async def async_add(x, y):
    await asyncio.sleep(0.1)
    return x + y

@pytest.mark.asyncio
async def test_async_add():
    print("开始测试")
    with open('D:\下载\金庸全集TXT\新.txt', 'r', encoding='utf-8') as f:
        content = f.read()

    # print(content)
    document = content
    node = RagNode()
    milvus_node = MilvusNode("test","ludingji")
    text_splitters = RecursiveCharacterTextSplitter(chunk_size=512, chunk_overlap=0)
    text = text_splitters.split_text(document)
    text = await remove_whitespace_list(text)
    top_ten = text[:10]
    test = ['这是文本1', "这是文本2"]
    print(text[0])
    embeddings = await node.text_to_embedding_documents_bge(text)
    data = [
        embeddings,
        text
    ]
    await milvus_node.insert_into_data(data)
    print("结束")
    # print(len(text))
    # print(len(embeddings))
    # await async_to_embedding()

