from langchain_ollama import OllamaLLM

llm = OllamaLLM(model="qwen3:8b", reasoning=True)

# 调用 generate_prompt 而不是 invoke
res = llm.generate_prompt([llm._convert_input("你好")])

print(res.generations[0][0].text)   # 输出文本
print(res)               # 这里可能包含 token_usage
