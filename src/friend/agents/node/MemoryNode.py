from src.friend.app.db.MemoryDB import create_memory_db,MemoryDB


# 这个是关于长期记忆的节点
class MemoryNode:
    def __init__(self,memory_db:MemoryDB):
        self.memory_db = memory_db
    @classmethod
    async def create(cls):
        memory_db = await create_memory_db()
        return cls(memory_db)

async def get_memory_node()-> MemoryNode:
    if not hasattr(get_memory_node,"instance"):
        get_memory_node.instance = await MemoryNode.create()
    return get_memory_node.instance