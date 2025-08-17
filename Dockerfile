# Stage 0: 构建依赖
FROM python:3.12-slim AS builder

# 基本系统依赖（如需，按实际情况增减）
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# 安装 Poetry（指定版本可控）
ENV POETRY_VERSION=2.1.3
RUN curl -sSL https://install.python-poetry.org | python - --version ${POETRY_VERSION}
ENV PATH="/root/.local/bin:${PATH}"

# 设置工作目录
WORKDIR /app

# 先只拷贝元数据文件以利用缓存
COPY pyproject.toml poetry.lock* ./

# 安装依赖（生产环境常用 --no-dev）
RUN poetry install --no-root --no-interaction --no-ansi

# Stage 1: 生产镜像
FROM python:3.12-slim

# 复制 Poetry 生成的依赖内容到最终镜像
WORKDIR /app
ENV PATH="/root/.local/bin:${PATH}"

# 安装必要的系统依赖（如果 Stage 0 需要的库在这里也要安装）
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*

# 将依赖复制进来
COPY --from=builder /usr/local/lib/python*/site-packages /usr/local/lib/python*/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# 复制代码
COPY . .

# 运行入口（按你的实际应用改写）
CMD ["python", "src/friend/runserver.py"]