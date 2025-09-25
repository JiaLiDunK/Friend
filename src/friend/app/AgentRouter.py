from fastapi import APIRouter, Depends

from src.friend.agents.node.DataBaseNode import DataBaseNode, get_data_base_node

agentRouter = APIRouter()



@agentRouter.get("/test")
async def one_test_one(data:DataBaseNode = Depends(get_data_base_node)):
    await data.should_create_book_vectors()
    return {"message": "Hello, World!::"}