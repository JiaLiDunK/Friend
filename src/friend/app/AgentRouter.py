from fastapi import APIRouter, Depends

from src.friend.agents.node.DataBaseNode import DataBaseNode, get_data_base_node

agentRouter = APIRouter()



@agentRouter.post("/test")
async def test(data:DataBaseNode = Depends(get_data_base_node)):
    await data.should_create_knowledge_base()
    return {"message": "Hello, World!::"}