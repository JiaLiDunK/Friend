

# 这个是关于长期记忆的节点
class MemoryNode:
    def __init__(self,nulls):
        self.nulls = nulls
    @classmethod
    async def create(cls):
        nulls = "124"
        return cls(nulls)
