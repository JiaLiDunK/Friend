# 使用 Python 3.12 作为基础镜像
FROM python:3.12-slim AS base

# 安装 Poetry
RUN pip install "poetry==2.1.3"

# 设置工作目录
WORKDIR /app

# 复制所有项目文件（包括 src/friend）
COPY . .

# 确保 Poetry 不创建虚拟环境
RUN poetry config virtualenvs.create false

# 安装依赖（不包括 dev）
RUN poetry install --no-root

# 映射端口
EXPOSE 8080

# 启动服务
CMD ["poetry", "run", "uvicorn", "src.friend.app:app", "--host", "0.0.0.0", "--port", "8080"]
