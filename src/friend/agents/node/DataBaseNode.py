from langchain.agents import create_openai_tools_agent, AgentExecutor
from langchain_community.chat_models import ChatTongyi
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from loguru import logger

from src.friend.agents.node.MilvusNode import create_milvus_node
from src.friend.agents.node.RagNode import get_rag_node
from src.friend.agents.state.DataBaseState import DataBaseState
from src.friend.agents.tools.DataBaseTools import DataBaseTools
from src.friend.app.db.BookVectorsDB import create_book_vectors_db
from src.friend.app.db.ChunkDB import create_chunk_db
from src.friend.app.db.KnowledgeBaseDB import create_knowledge_base_db
from src.friend.app.db.PromptDB import create_prompt_db
from src.friend.config.SettingConfig import settings


class DataBaseNode:
    def __init__(self,knowledge_base_db,book_vectors_db,prompt_db,system_prompt,milvus_node,chunk_db,rag_node):
        self.llm = ChatTongyi(
            model=settings.MODEL,
            api_key=settings.API_KEY_ALI,  # 生成多样性控制
            model_kwargs={
                "temperature": 0.0  # 让回答统一
            }
        )
        self.knowledge_base_db = knowledge_base_db
        self.book_vectors_db = book_vectors_db
        self.milvus_node = milvus_node
        self.prompt_db = prompt_db
        self.chunk_db = chunk_db
        self.rag_node = rag_node
        # 创建工具
        db_tools = DataBaseTools(knowledge_base_db,book_vectors_db)
        self.tools = db_tools.get_tools()
        # 2. 定义 prompt
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("user", "{input}"),
            MessagesPlaceholder("agent_scratchpad"),
        ])
        # 创建agent和executor
        self.save_database_agent  = create_openai_tools_agent(self.llm,self.tools,self.prompt)
        self.save_database_executor = AgentExecutor(agent=self.save_database_agent, tools=self.tools, verbose=True)

    @classmethod
    async def create(cls):
        knowledge_base_db = await create_knowledge_base_db()
        book_vectors_db = await create_book_vectors_db()
        prompt_db = await create_prompt_db()
        milvus_node = await create_milvus_node()
        chunk_db = await  create_chunk_db()
        rag_node = await get_rag_node()
        # 从数据库中读取system提示词
        system_prompt = await prompt_db.get_prompt_by_id(4)
        return cls(knowledge_base_db,book_vectors_db,prompt_db,system_prompt,milvus_node,chunk_db,rag_node)

    async def should_create_knowledge_base(self,data:DataBaseState):
        """判断是否需要创建知识库,如果需要知识库,则返回对应的书籍"""
        knowledge_base_list = await self.knowledge_base_db.get_data_to_ai()
        books_db_list = await self.book_vectors_db.get_data_to_ai()
        message =  await self.prompt_db.get_prompt_by_id(2)
        message += "\n【已有的知识库信息】"
        for item in knowledge_base_list:
            message += f"\n{item}"
        message += "\n【下面是相关的书籍】:"
        for item in books_db_list:
           message += f"\n{item}"
        logger.info(f"打印create_knowledge_base:\n{message}")
        result_out = await self.llm.ainvoke(message)
        data.message = result_out.content
        logger.info(f"回复的书籍:\n{data.message}")
        return data
    async def should_update_book_vectors(self,data:DataBaseState):
        """分配书籍向量的知识库"""
        knowledge_base_list = await self.knowledge_base_db.get_data_to_ai()
        books_db_list = await self.book_vectors_db.get_data_to_ai()
        message = await self.prompt_db.get_prompt_by_id(3)
        message += "\n已有的知识库:"
        for item in knowledge_base_list:
            message += f"\n{item}"
        message += "\n待分类书籍:"
        for item in books_db_list:
            message += f"\n{item}"
        logger.info(f"生成的提示词信息:\n{message}")
        result_out = await self.llm.ainvoke(message)
        data.message = result_out.content
        logger.info(f"回复的信息:\n{data.message}")
        return data

    async def create_data_base(self,data:DataBaseState):
        """往数据库里面进行增删改查"""
        logger.info(f"进入创建的页面:\n{data.message}")
        await self.save_database_executor.ainvoke({"input":data.message})

    async def judge_create(self,data:DataBaseState):
        """判断知识库是否需要更新"""
        if len(data.message) < 10:
            return 'end'
        else:
            return 'continue'
    async def data_to_chunk(self):
        """把所有标注了知识库id和type_id为8的书籍向量化"""
        # 1.获取所有知识库和相关集合的信息
        knowledge_base_list = await self.knowledge_base_db.get_data_to_ai()
        # 2.创建知识库和集合
        for item in knowledge_base_list:
            await self.milvus_node.create_database(item.data_base)
            await self.milvus_node.create_collection(item.data_base,item.collection)
        # 3.向量化相关的书籍
        book_list = await self.book_vectors_db.get_uuid_list()
        # 暂时不进行下述的操作
        for item in book_list:
            logger.info(f"输出的是item的信息{item}")
            data_list = await self.chunk_db.get_content_by_uuid(item.uuid)
            # 向量化，插入进数据库
            embeddings = await self.rag_node.text_to_embedding_documents_bge(data_list)
            knowledge_base_data = await self.knowledge_base_db.get_data_by_id(item.knowledge_base_id)
            data_to_insert = [
                {"vector": vec, "content": text}
                for vec, text in zip(embeddings, data_list)
            ]
            logger.info(f"{len(embeddings)}={len(data_list)}={len(embeddings[0])}")
            # 4.将数据插入进数据库中
            await self.milvus_node.insert_into_data(data=data_to_insert,data_base_name=knowledge_base_data.data_base,collection_name=knowledge_base_data.collection)
            logger.info(f"插入完成{item}")


async def get_data_base_node()-> DataBaseNode:
    if not hasattr(get_data_base_node,"instance"):
        get_data_base_node.instance = await DataBaseNode.create()
    return get_data_base_node.instance