#!/bin/bash

# EvoFlow 启动脚本

echo "Starting EvoFlow services..."

# 检查Docker是否运行
if ! docker info > /dev/null 2>&1; then
    echo "Error: Docker is not running. Please start Docker first."
    exit 1
fi

# 创建日志目录
mkdir -p logs

# 启动服务
echo "Starting services with Docker Compose..."
docker-compose up -d

# 等待服务启动
echo "Waiting for services to start..."
sleep 10

# 检查服务状态
echo "Checking service status..."
docker-compose ps

# 显示日志
echo "Showing recent logs..."
docker-compose logs --tail=20

echo "EvoFlow services started successfully!"
echo "API Documentation: http://localhost:8000/docs"
echo "Health Check: http://localhost:8000/health"
