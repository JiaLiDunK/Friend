import json
import asyncio
from typing import Dict, Any

# =========================
# 1. Skill 基类
# =========================
class BaseSkill:
    name: str = ""
    description: str = ""

    async def run(self, params: Dict[str, Any]) -> Any:
        raise NotImplementedError


# =========================
# 2. Skills 实现
# =========================
class WeatherSkill(BaseSkill):
    name = "get_weather"
    description = "查询某个城市的天气，例如：北京天气"

    async def run(self, params):
        city = params.get("city", "未知城市")
        return f"{city} 今天天气晴朗 ☀️ 25°C"


class MathSkill(BaseSkill):
    name = "calculate"
    description = "执行数学计算，例如：12 * 8"

    async def run(self, params):
        expr = params.get("expression", "")
        try:
            result = eval(expr)
            return f"计算结果：{result}"
        except Exception as e:
            return f"计算失败: {e}"


# =========================
# 3. Skill 注册中心
# =========================
class SkillRegistry:
    def __init__(self):
        self.skills = {}

    def register(self, skill: BaseSkill):
        self.skills[skill.name] = skill

    def get(self, name: str):
        return self.skills.get(name)

    def list_skills(self):
        return [
            {
                "name": s.name,
                "description": s.description
            }
            for s in self.skills.values()
        ]


# =========================
# 4. Mock LLM（可替换）
# =========================
class MockLLM:
    """
    没有接入真实 LLM 时用这个
    """

    async def ainvoke(self, prompt: str):
        user_input = prompt.split("用户问题：")[-1].strip()

        # 简单规则模拟 LLM 决策
        if "天气" in user_input:
            return MockResp(json.dumps({
                "skill": "get_weather",
                "params": {"city": "北京"}
            }))

        if any(x in user_input for x in ["+", "-", "*", "/"]):
            return MockResp(json.dumps({
                "skill": "calculate",
                "params": {"expression": user_input}
            }))

        return MockResp(json.dumps({
            "skill": None,
            "params": {}
        }))


class MockResp:
    def __init__(self, content):
        self.content = content


# =========================
# 5. Prompt 构造
# =========================
def build_prompt(user_input, skills):
    return f"""
你是一个智能助手，可以调用工具完成任务。

可用工具：
{json.dumps(skills, ensure_ascii=False, indent=2)}

请根据用户问题选择最合适的工具，并返回 JSON：

格式：
{{
  "skill": "技能名",
  "params": {{参数}}
}}

如果不需要工具：
返回：
{{"skill": null, "params": {{}}}}

用户问题：
{user_input}
"""


# =========================
# 6. LLM 路由
# =========================
async def llm_route(llm, user_input, registry: SkillRegistry):
    prompt = build_prompt(user_input, registry.list_skills())

    resp = await llm.ainvoke(prompt)

    try:
        data = json.loads(resp.content)
        return data
    except Exception as e:
        print("LLM解析失败:", e)
        return {"skill": None, "params": {}}


# =========================
# 7. 执行器
# =========================
async def execute(user_input, llm, registry: SkillRegistry):
    route = await llm_route(llm, user_input, registry)

    skill_name = route.get("skill")
    params = route.get("params", {})

    print(f"\n🧠 LLM决策: {route}")

    if not skill_name:
        return "🤖 LLM认为不需要调用工具"

    skill = registry.get(skill_name)

    if not skill:
        return f"❌ 未找到技能: {skill_name}"

    result = await skill.run(params)

    return f"✅ Skill结果: {result}"


# =========================
# 8. 初始化
# =========================
def init_registry():
    registry = SkillRegistry()
    registry.register(WeatherSkill())
    registry.register(MathSkill())
    return registry


# =========================
# 9. CLI 测试入口
# =========================
async def main():
    registry = init_registry()

    # 👉 这里可以换成你的真实 LLM
    from langchain_community.chat_models import ChatTongyi
    llm = ChatTongyi(
            model="qwen-plus",
            api_key="sk-12d7440948d94e27a9597ff57fe2a8c7",
            model_kwargs={
                "temperature": 0.0  # 让回答统一
            },
        )

    print("🚀 Agent Demo 启动（输入 exit 退出）\n")

    while True:
        user_input = input("👤 你：")

        if user_input.lower() in ["exit", "quit"]:
            break

        result = await execute(user_input, llm, registry)

        print("🤖 系统：", result)


if __name__ == "__main__":
    asyncio.run(main())