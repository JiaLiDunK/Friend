from langchain_community.chat_models import ChatTongyi
from langchain_core.messages import SystemMessage, HumanMessage

llm = ChatTongyi(
            model="qwen-vl-ocr",
            api_key="sk-",  # 生成多样性控制
            model_kwargs={
                "temperature": 0.7  # 让回答统一
            }
        )
messages = [
    SystemMessage(content="你是一个图像描述助手。"),
    HumanMessage(content="请描述这张图片的内容。")
]
result = llm.invoke(messages)
print(result)