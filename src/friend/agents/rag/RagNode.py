from typing import List

from langchain_ollama import OllamaEmbeddings


class RagNode:
    def __init__(self):
        self.bge_m3 = OllamaEmbeddings(
            model="bge-m3",
        )

    async def text_to_embedding_documents_bge(self,text:List[str]):
        """把一个列表的字符串转化成向量"""
        return  self.bge_m3.embed_documents(text)

    async def text_to_embedding_query_bge(self,text:str):
        """把一个字符串转化成向量"""
        return self.bge_m3.embed_query(text)

