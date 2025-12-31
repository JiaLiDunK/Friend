import asyncio
import json
import os
import uuid
from datetime import datetime
from typing import List

from langchain.agents import create_openai_tools_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_ollama import OllamaLLM
from loguru import logger

from src.friend.agents.tools.DataScoreTools import DataScoreTools
from src.friend.app.db.BooksDB import create_books_db_by_load
from src.friend.app.db.ChunkDB import create_chunk_db, create_chunk_db_by_load
from src.friend.app.db.JoinLinkDB import create_join_link_load
from src.friend.app.db.PromptDB import create_prompt_db_by_load
from src.friend.app.db.QApairsDB import create_qa_pairs_load
from src.friend.entity.ai.AIResponseMessage import GeneratedData, ScoreData
from src.friend.entity.po.Books import Books
from src.friend.entity.po.Chunk import Chunk
from src.friend.entity.po.QApairs import QApairs
from src.friend.entity.vo.AddForm import AddBooks
from src.friend.utils.StringUtils import split_all_files_in_dir, load_chunk_document, clean_text, remove_substring, \
    chunk_docs, chunk_array, compress_newlines


class ReadNode:
    def __init__(self,books_db,chunk_db,join_link_db,qa_pairs_db,prompt_db):
        self.books_db = books_db
        self.chunk_db = chunk_db
        self.join_link_db = join_link_db
        self.qa_pairs_db = qa_pairs_db
        self.prompt_db = prompt_db
        self.ollamaLLm = OllamaLLM(
        model="huihui_ai/qwen3-abliterated:8b",
        reasoning=True,
        temperature=0.2
    )

    @classmethod
    async def create(cls):
        books_db = await create_books_db_by_load()
        chunk_db = await create_chunk_db_by_load()
        join_link_db = await create_join_link_load()
        qa_pairs_db = await create_qa_pairs_load()
        prompt_db = await create_prompt_db_by_load()
        return cls(books_db, chunk_db,join_link_db,qa_pairs_db,prompt_db)
    async  def clear_string_task(self,text:str):
        """清除所有文件中的指定内容"""
        logger.info("开始清除")
        data_list = await self.chunk_db.select_all_uuid()
        task_list = await chunk_array(data_list)
        tasks = [asyncio.create_task(self.clear_string(text,task)) for task in task_list]
        # 等待任务完成
        await asyncio.gather(*tasks)
        logger.info("清除完成")
    async def clear_string(self,text:str,uuid_list:List[str]):
        """清除指定uuid中的指定内容"""
        chunk_db = await create_chunk_db()
        for uuids in uuid_list:
           chunk_list = await self.chunk_db.get_data_uuid(uuids)
           for chunk in chunk_list:
               chunk.content = await remove_substring(chunk.content, text)
           await chunk_db.update_data_list(chunk_list)
    async def repartition_task(self):
        """重新分割所有文件中的内容"""
        logger.info("开始重新分割")
        data_list = await self.chunk_db.select_all_uuid()
        task_list = await chunk_array(data_list)
        tasks = [asyncio.create_task(self.repartition_uuid(task)) for task in task_list]
        # 等待任务完成
        await asyncio.gather(*tasks)
        logger.info("重新分割完成")
    async def repartition_uuid(self,uuid_list:List[str]):
        """重新分割指定uuid文档中的内容"""
        for uuids in uuid_list:
            chunk_list = await self.chunk_db.get_data_uuid(uuids)
            all_docs = ""
            for chunk in chunk_list:
                all_docs += chunk.content
            docs = await chunk_docs(all_docs)
            chunk_list: List[Chunk] = []
            i = 1
            for doc in docs:
                chunk = Chunk(content=doc.page_content, order_id=i, title_id=1, uuid=uuids, type_id=2)
                chunk_list.append(chunk)
                i += 1
            await self.chunk_db.update_data_list(chunk_list)

    async def read_path(self,data:AddBooks):
        """多线程启动的---分割指定目录下的文本文件"""
        arr = await split_all_files_in_dir(data.path)
        tasks = [asyncio.create_task(self.read_and_save(paths,data)) for paths in arr]
        # 等待任务完成
        await asyncio.gather(*tasks)
        logger.info("读取完成")

    async def read_and_save(self,paths: List[str],data:AddBooks):
        """分割保存指定目录下的文本文件"""
        # 防止并发复用
        books_db = await create_books_db_by_load()
        chunk_db = await create_chunk_db_by_load()
        for path in paths:
            try:
                sole_id = str(uuid.uuid4())
                docs = await load_chunk_document(path,
                                                 chunk_size=612,
                                                 chunk_overlap=100,
                                                 separators=[
                                                     "\n\n",  # 段落
                                                     "\n",  # 单换行
                                                     "。", "！", "？", "；",  # 中文句号/感叹号/问号/分号
                                                     ".", "!", "?", ";",  # 英文句号/感叹号/问号/分号
                                                     "，", ",",  # 中文、英文逗号
                                                     "：", ":",  # 中文、英文冒号
                                                     " ",  # 空格
                                                     ""  # 最后兜底（强制切割）
                                                 ])
                filename = os.path.basename(path)
                logger.info(f"开始处理文件: {filename}, uuid={sole_id}")
                # 默认 type_id = 4
                type_id = 4
                # 如果 docs 太少，就改 type_id
                if not docs:
                    type_id = 5  # 你需要的 type_id 值
                elif len(docs) < 2:
                    type_id = 6
                book = Books(tittle=filename,format=filename.split('.')[-1],uuid=sole_id, type_id=type_id,use=data.use,remark=data.remark,insert_time= datetime.now())
                await books_db.insert_data(book)
                logger.info(f"插入 Book: {filename}")
                chunk_list: List[Chunk] = []
                i = 1
                for doc in docs:
                    safe_content = await clean_text(doc.page_content)
                    chunk = Chunk(content=safe_content, order_id=i, tittle_id=1, uuid=sole_id, type_id=2)
                    chunk_list.append(chunk)
                    i += 1
                await chunk_db.insert_list(chunk_list)
                logger.info(f"插入 {len(chunk_list)} 个 Chunks (文件: {filename})")
            except Exception as e:
                logger.error(f"处理文件失败: {path}, 错误: {e}", exc_info=True)
    async def clear_newline_character_task(self):
        """多线程启动的方法-把所有的内容中的多个\n变成一个"""
        logger.info("任务启动")
        data_list = await self.chunk_db.select_all_uuid()
        task_list = await chunk_array(data_list)
        tasks = [asyncio.create_task(self.clear_newline_character(task)) for task in task_list]
        # 等待任务完成
        await asyncio.gather(*tasks)
        logger.info("任务完成")
    async def clear_newline_character(self,uuid_list:List[str]):
        """把所有的内容中的多个\n变成一个"""
        # 防止并发复用
        chunk_db = await create_chunk_db()
        chunk_list:List[Chunk] = []
        for uuids in uuid_list:
            chunk_list = await chunk_db.get_data_uuid(uuids)
            for chunk in chunk_list:
                chunk.content = await compress_newlines(chunk.content)
        await chunk_db.update_data_list(chunk_list)

    async def start_create_lora_data(self,data_id:int,sole_uuid:str,sun_num:int):
        """开始"""
        result = await self.join_link_db.get_data_by_id(data_id)
        logger.info(f"本次的:{result}")
        if result.order_id >= result.sun_num:
            return "早已经生成"
        logger.info(f"开始执行任务{sole_uuid},总数{sun_num},排序{result.order_id}")
        for result.order_id in range(result.order_id,sun_num+1):
            data_str = await self.chunk_db.get_order_id_by_uuid(uuid=sole_uuid, order_id=result.order_id)
            content = data_str.content
            content_len = len(content)
            if content_len <= 50:
                continue
            if content_len > 400:
                level = 3
            elif content_len > 200:
                level = 2
            else:
                level = 1
            # 重试机制
            retries = 3
            for attempt in range(retries):
                try:
                    data_qa: GeneratedData = await self.create_lora_data(content, level)
                    break
                except Exception as e:
                    if attempt < retries - 1:
                        logger.warning(f"解析失败，等待 5 秒后重试... (第 {attempt + 1} 次)")
                        await asyncio.sleep(5)
                    else:
                        raise
            data_list:List[QApairs] = []
            i = 1
            for item in data_qa.generated:
                data_list.append(QApairs(question=item.question,answer=item.answer,chunk_id=data_str.id,insert_time=datetime.now(),order_id=i,sole_uuid=sole_uuid),)
                i+=1
            await self.qa_pairs_db.insert_list(data_list)
            await self.join_link_db.update_data_one(data_id,result.order_id+1)
        return "完成"

    async def create_lora_data(self,data: str, num_records: int)->GeneratedData:
        """单线程生成数据"""
        # 构造 prompt
        prompt = await self.prompt_template(data, num_records)
        # 调用模型
        result = await self.ollamaLLm.ainvoke(prompt)
        print(result)
        # 解析 JSON
        try:
            data_dict = json.loads(result)
            generated_data = GeneratedData(**data_dict)
        except json.JSONDecodeError:
            raise ValueError(f"模型输出不是合法 JSON: {result}")
        return generated_data

    async def create_data_score(self,data_id:int,sole_uuid:str):
        """给提问打分"""
        result = await self.join_link_db.get_data_by_id(data_id)
        logger.info(f"本次的:{result}")
        for result.scoring_completed in range(result.scoring_completed,result.sun_num+1):
            data_str = await self.chunk_db.get_order_id_by_uuid(uuid=sole_uuid, order_id=result.scoring_completed)
            data_list = await self.qa_pairs_db.get_data_by_uuid_order_id(uuid=sole_uuid, chunk_id=result.scoring_completed)
            for item in data_list:
                # 重试机制
                retries = 3
                for attempt in range(retries):
                    try:
                        data: ScoreData = await self.create_score(data_str.content,item)
                        await self.qa_pairs_db.update_score(data_id=data.id,score=data.score)
                        break
                    except Exception as e:
                        if attempt < retries - 1:
                            logger.warning(f"解析失败，等待 5 秒后重试... (第 {attempt + 1} 次)")
                            await asyncio.sleep(5)
                        else:
                            raise
                await self.join_link_db.update_data_one(data_id, result.scoring_completed + 1)
        return "打分完毕"
    async def create_score(self,data_str:str,data:QApairs)->ScoreData:
        """给打分"""
        system_prompt = await self.prompt_db.get_prompt_by_id(7)
        system_prompt += "原文:"+data_str+" id:"+str(data.id)+" 问题:"+data.question+" 回答:"+data.answer
        result = await self.ollamaLLm.ainvoke(system_prompt)
        logger.info(result)
        try:
            data_dict = json.loads(result)
            score_data = ScoreData(**data_dict)
        except json.JSONDecodeError:
            raise ValueError(f"模型输出不是合法 JSON: {result}")
        return score_data

    async def prompt_template(self,data: str, num_records: int) -> str:
        return f"""
            你是一个【数据生成助手】，只负责生成结构化问答数据。
            请根据以下上下文内容，生成 {num_records} 条【问答对】。
            【上下文】
            {data}
            【严格输出规则（非常重要）】
            1. 只能输出一个 JSON 对象，不要输出任何解释性文字
            2. JSON 必须严格符合以下结构，不允许新增、删除或翻译任何字段名
            3. 字段名必须 **只允许使用英文**：
               - question
               - answer
            4. 不允许出现以下字段名（即使语义相同也不允许）：
               - 问题
               - 答案
               - 提问
               - 回答
            5. 每一条 generated 中的元素都必须同时包含 question 和 answer
            6. 不允许出现 null、缺失字段或多余字段
            7. 如果无法生成合格数据，也必须返回合法 JSON，generated 为空数组 []
            
            【唯一允许的输出格式示例】
            {{
              "generated": [
                {{
                  "question": "示例问题",
                  "answer": "示例回答"
                }}
              ]
            }}
            现在开始生成数据。
    """
async def get_read_node() -> ReadNode:
    """
    FastAPI 依赖注入函数，用于获取单例的 ReadNode 实例。
    - 第一次调用时，会通过 `ReadNode.create()` 初始化一个实例，并绑定到函数属性上。
    - 后续调用时，直接复用之前创建的实例（保证全局只有一个 ReadNode）。
    - 好处：避免在每个接口函数里都重复 `await ReadNode.create()`。
    """
    # 判断这个函数对象是否已经有一个 "instance" 属性
    if not hasattr(get_read_node, "instance"):
        # 如果没有，就创建一个新的 ReadNode 实例并缓存起来
        get_read_node.instance = await ReadNode.create()

    # 返回全局唯一的 ReadNode 实例
    return get_read_node.instance