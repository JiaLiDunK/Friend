from mcp.server.fastmcp import FastMCP
import asyncio
from typing import Any, Dict
mcp = FastMCP("weather_server")
def get_weather(city: str, request: Dict[str, Any] = None) -> str:
    """获取指定城市的天气（从 metadata 拿 sole_id）"""

    sole_id = "NO_ID"

    # ✅ 从 metadata 获取
    if request and isinstance(request, dict):
        metadata = request.get("metadata", {})
        sole_id = metadata.get("sole_id", "NO_ID")

    print(f"[TOOL] sole_id={sole_id}, city={city}")

    return f"在 {city} 总是阳光明媚！"



@mcp.tool()
def weather(city: str, request: Dict[str, Any] = None) -> str:
    return get_weather(city, request)
if __name__ == "__main__":
    mcp.run()