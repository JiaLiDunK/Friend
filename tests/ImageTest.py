import os
import base64
import requests
from datetime import datetime
from openai import OpenAI

'''
内容识别完成，测试通过,date:250730
'''

class AliBailianImageService:
    def __init__(self, configuration):
        self.configuration = configuration

    def get_api_key(self):
        api_key = ""
        # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key = "sk-xxx"
        if not api_key:
            print("API Key 未设置。请确保环境变量 'DASHSCOPE_API_KEY' 已设置。")
            return None
        return api_key

    def get_image_base64_string_and_save(self, image_url):
        response = requests.get(image_url)
        if response.status_code != 200:
            raise Exception(f"Failed to download image: {response.status_code}")
        image_data = response.content
        encoded_image = base64.b64encode(image_data).decode('utf-8')
        return encoded_image

    def send_post_request(self, url, json_content, api_key):
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        response = requests.post(url, data=json_content, headers=headers)
        response_body = response.text
        self.write_response_to_log(response_body)
        if 200 <= response.status_code < 300:
            return response_body
        else:
            return f"请求失败: {response.status_code}"

    def write_response_to_log(self, response_body):
        log_file_path = "../convert_files/Logs/response.log"
        log_dir = os.path.dirname(log_file_path)
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        with open(log_file_path, 'a') as f:
            f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Response Body: {response_body}\n")

    def image_to_base64(self, file_path):
        with open(file_path, "rb") as image_file:
            # 读取图片二进制数据
            image_data = image_file.read()
            # 转换为Base64编码字节
            base64_bytes = base64.b64encode(image_data)
            # 转换为UTF-8字符串
            base64_string = base64_bytes.decode("utf-8")
        return base64_string

    def get_results(self, file_path):
        api_key = self.get_api_key()
        print("api_key>>", api_key)
        if not api_key:
            return None

        encoded_image = self.image_to_base64(file_path)

        client = OpenAI(
            # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx",
            api_key=api_key,
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        )

        # 提交一个 chat completion 请求，用图片数据和简单文本进行指令交互
        # 下面的结构请根据你实际的模型端点要求进行调整
        completion = client.chat.completions.create(
            model="qwen-vl-plus",
            # 此处以qwen-vl-plus为例，可按需更换模型名称。模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
            messages=[{"role": "user", "content": [
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{encoded_image}"}},
                {"type": "text", "text": "识别图片内容，只输出图片内容"},
            ]}]
        )
        # 输出模型返回的 JSON 形式字符串（依赖库实现）
        try:
            print(completion.model_dump_json())
            return completion
        except AttributeError:
            # 某些版本可能没有 model_dump_json，给出备用输出
            return completion

if __name__ == "__main__":
    img_file_path = "D:\图片练手\表情包.png"
    # 示例配置
    config = {
        "DASHSCOPE_API_KEY": ""
    }
    service = AliBailianImageService(config)
    result = service.get_results(img_file_path)
    if result:
        print("Result:", result)