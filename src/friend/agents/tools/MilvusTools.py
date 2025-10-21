from src.friend.agents.node.MilvusNode import create_milvus_node, MilvusNode


class MilvusTools:
    def __init__(self,milvus_node:MilvusNode):
        self.milvus_node = milvus_node
    @classmethod
    async def create(cls):
        milvus_node = await create_milvus_node()
        return cls(milvus_node)