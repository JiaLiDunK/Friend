from langchain.agents import create_openai_tools_agent, AgentExecutor
from langchain_community.chat_models import ChatTongyi
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from loguru import logger
from src.friend.agents.state.DataBaseState import DataBaseState
from src.friend.app.db.PromptDB import create_prompt_db
from src.friend.agents.tools.DataBaseTools import DataBaseTools
from src.friend.app.db.BookVectorsDB import create_book_vectors_db
from src.friend.app.db.KnowledgeBaseDB import create_knowledge_base_db
from src.friend.config.SettingConfig import settings


class DataBaseNode:
    def __init__(self,knowledge_base_db,book_vectors_db,prompt_db,system_prompt):
        self.llm = ChatTongyi(
            model=settings.MODEL,
            api_key=settings.API_KEY_ALI
        )
        self.knowledge_base_db = knowledge_base_db
        self.book_vectors_db = book_vectors_db
        self.prompt_db = prompt_db
        # 创建工具
        self.tools = [DataBaseTools.insert_knowledge_base,
                      DataBaseTools.insert_book_vectors]
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
        # 从数据库中读取system提示词
        system_prompt = await prompt_db.get_prompt_by_id(2)
        return cls(knowledge_base_db,book_vectors_db,prompt_db,system_prompt)

    async def should_create_knowledge_base(self,data:DataBaseState):
        """判断是否需要创建知识库,如果需要知识库,则返回对应的书籍"""
        knowledge_base_list = await self.knowledge_base_db.get_data_to_ai()
        books_db_list = await self.book_vectors_db.get_data_to_ai()
        message =  await self.prompt_db.get_prompt_by_id(2)
        message += "下面是已有的知识库相关的信息"
        for item in knowledge_base_list:
            message += f"\n{item}"
        message += "\n下面是相关的书籍:"
        logger.info(len(books_db_list))
        for item in books_db_list:
           message += f"\n{item}"
        logger.info(f"打印create_knowledge_base{message}")
        result_out = await self.llm.ainvoke(message)
        data.message = result_out.content
        return data
    async def should_create_book_vectors(self,data:DataBaseState):
        """判断是否需要创建书籍向量"""
        knowledge_base_list = await self.knowledge_base_db.get_data_to_ai()
        books_db_list = await self.book_vectors_db.get_data_to_ai()
        message = await self.prompt_db.get_prompt_by_id(3)
        message += "\n下面是已有的知识库相关的信息"
        for item in knowledge_base_list:
            message += f"\n{item}"
        message += "\n下面是相关的书籍:"
        logger.info(len(books_db_list))
        for item in books_db_list:
            message += f"\n{item}"
        result_out = await self.llm.ainvoke(message)
        data.message = result_out.content
        return data

    async def create_knowledge_base(self,data:DataBaseState):
        """往数据库里面进行增删改查"""
        pass


    async def judge_create(self,data:DataBaseState):
        """判断知识库是否需要更新"""
        logger.info(f"进入判断:{data.message}")
        if len(data.message) < 10:
            return 'end'
        else:
            return 'continue'

async def get_data_base_node()-> DataBaseNode:
    if not hasattr(get_data_base_node,"instance"):
        get_data_base_node.instance = await DataBaseNode.create()
    return get_data_base_node.instance