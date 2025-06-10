# 使用官方Python 3.11镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# 安装uv
RUN pip install uv

# 复制项目文件
COPY pyproject.toml ./
COPY uv.lock* ./

# 创建虚拟环境并安装依赖
RUN uv venv .venv
RUN uv pip install -e ".[dev]"

# 复制应用代码
COPY . .

# 设置环境变量
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app"

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "evoflow.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
