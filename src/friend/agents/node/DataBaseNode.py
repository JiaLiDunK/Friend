from langchain.agents import create_openai_tools_agent, AgentExecutor
from langchain_community.chat_models import ChatTongyi
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from src.friend.app.db.PromptDB import create_prompt_db
from src.friend.agents.tools.DataBaseTools import DataBaseTools
from src.friend.app.db.BookVectorsDB import create_book_vectors_db
from src.friend.app.db.KnowledgeBaseDB import create_knowledge_base_db
from src.friend.config.SettingConfig import settings


class DataBaseNode:
    def __init__(self,knowledge_base_db,book_vectors_db,prompt_db,system_prompt):
        self.llm = ChatTongyi(
            model=settings.TONGYI_MODEL,
            api_key=settings.TONGYI_API_KEY
        )
        self.knowledge_base_db = knowledge_base_db
        self.book_vectors_db = book_vectors_db
        self.prompt_db = prompt_db
        # 创建工具
        self.tools = [DataBaseTools.insert_knowledge_base,DataBaseTools.insert_book_vectors]
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
    async def create_knowledge_base(self,data:DataBaseState):
        """创建知识库的"""
        pass
    async def judge_knowledge_base(self,data:DataBaseState):
        """判断知识库是否需要更新"""
        if len(data['message']) < 10:
            return 'end'
        else:
            return 'continue'