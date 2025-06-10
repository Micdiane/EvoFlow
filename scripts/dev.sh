#!/bin/bash

# EvoFlow 开发环境启动脚本

echo "Starting EvoFlow development environment..."

# 检查uv是否安装
if ! command -v uv &> /dev/null; then
    echo "Installing uv..."
    pip install uv
fi

# 创建虚拟环境（如果不存在）
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    uv venv
fi

# 安装依赖
echo "Installing dependencies..."
uv pip install -e ".[dev]"

# 启动数据库和Redis
echo "Starting database and Redis..."
docker-compose up -d postgres redis

# 等待数据库启动
echo "Waiting for database to be ready..."
sleep 5

# 运行数据库迁移（如果需要）
echo "Running database migrations..."
# alembic upgrade head

# 启动开发服务器
echo "Starting development server..."
source .venv/bin/activate
uvicorn evoflow.main:app --host 0.0.0.0 --port 8000 --reload
