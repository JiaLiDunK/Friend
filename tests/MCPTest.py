# minimal_mcp_inject_demo.py
# 说明：演示两种注入方式的包装器：Header 注入 与 Payload(metadata) 注入
# 请根据你实际的 MCP 客户端 API 调整 call_tool 的签名

from typing import Any, Dict

# 假设的原始 MCP 客户端（替换为真实的 MultiServerMCPClient）
class FakeMCPClient:
    def __init__(self, server_url: str):
        self.server_url = server_url

    # 假设的调用接口：tool_name, payload, 可选 headers
    def call_tool(self, tool_name: str, payload: Dict[str, Any], headers: Dict[str, str] = None) -> Dict[str, Any]:
        # 这里仅模拟返回，真实实现会发 HTTP 或其它传输
        return {
            "tool": tool_name,
            "received_payload": payload,
            "received_headers": headers or {},
            "result": f"ok from {self.server_url}"
        }

# 包装器 A：在 HTTP headers 注入隐藏值（适用于 HTTP-based MCP）
class HeaderInjectingMCPClient:
    def __init__(self, inner_client: FakeMCPClient, secret_value: str, header_name: str = "X-Internal-Secret"):
        self.inner = inner_client
        self.secret_value = secret_value
        self.header_name = header_name

    def call_tool(self, tool_name: str, payload: Dict[str, Any], headers: Dict[str, str] = None) -> Dict[str, Any]:
        headers = dict(headers or {})
        headers[self.header_name] = self.secret_value
        # 转发到真实客户端
        return self.inner.call_tool(tool_name, payload, headers=headers)

# 包装器 B：在 payload 的 metadata 字段注入隐藏值（适用于非 HTTP 或 body-based 协议）
class PayloadInjectingMCPClient:
    def __init__(self, inner_client: FakeMCPClient, secret_key: str = "internal_secret"):
        self.inner = inner_client
        self.secret_key = secret_key

    def call_tool(self, tool_name: str, payload: Dict[str, Any], headers: Dict[str, str] = None) -> Dict[str, Any]:
        # 不破坏原 payload，复制并注入 metadata
        payload_copy = dict(payload)
        meta = dict(payload_copy.get("metadata") or {})
        meta[self.secret_key] = "SENSITIVE_VALUE_123"  # 这里注入隐藏值
        payload_copy["metadata"] = meta
        return self.inner.call_tool(tool_name, payload_copy, headers=headers)

# ---------- 使用示例 ----------
def main():
    # 原始客户端（替换为真实 MultiServerMCPClient(...))
    base_client = FakeMCPClient("http://localhost:8000")

    # 方式一：Header 注入
    header_client = HeaderInjectingMCPClient(base_client, secret_value="top-secret-token")
    resp1 = header_client.call_tool("math_tool", {"query": "2+2"})
    print("Header-injected response:", resp1)

    # 方式二：Payload metadata 注入
    payload_client = PayloadInjectingMCPClient(base_client, secret_key="x_internal_secret")
    resp2 = payload_client.call_tool("db_query", {"sql": "SELECT * FROM users LIMIT 1"})
    print("Payload-injected response:", resp2)

if __name__ == "__main__":
    main()
