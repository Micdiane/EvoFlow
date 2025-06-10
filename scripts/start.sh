#!/bin/bash

# EvoFlow 启动脚本

echo "🚀 Starting EvoFlow services..."

# 检查Docker是否运行
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker is not running. Please start Docker first."
    exit 1
fi

# 创建必要的目录
echo "📁 Creating directories..."
mkdir -p logs
mkdir -p alembic/versions

# 启动数据库和Redis
echo "🗄️  Starting database and Redis..."
docker-compose up -d postgres redis

# 等待数据库启动
echo "⏳ Waiting for database to be ready..."
sleep 10

# 检查数据库连接
echo "🔍 Checking database connection..."
max_attempts=30
attempt=1

while [ $attempt -le $max_attempts ]; do
    if docker-compose exec -T postgres pg_isready -U evoflow > /dev/null 2>&1; then
        echo "✅ Database is ready!"
        break
    fi

    if [ $attempt -eq $max_attempts ]; then
        echo "❌ Database failed to start after $max_attempts attempts"
        exit 1
    fi

    echo "   Attempt $attempt/$max_attempts - waiting for database..."
    sleep 2
    ((attempt++))
done

# 运行数据库迁移
echo "🔄 Running database migrations..."
if command -v uv &> /dev/null; then
    uv run alembic upgrade head
else
    docker-compose exec backend alembic upgrade head
fi

# 初始化数据
echo "📊 Initializing default data..."
if command -v uv &> /dev/null; then
    uv run python scripts/init_data.py
else
    docker-compose exec backend python scripts/init_data.py
fi

# 启动所有服务
echo "🌐 Starting all services..."
docker-compose up -d

# 等待服务启动
echo "⏳ Waiting for all services to start..."
sleep 15

# 检查服务状态
echo "📋 Checking service status..."
docker-compose ps

# 健康检查
echo "🏥 Performing health check..."
max_attempts=10
attempt=1

while [ $attempt -le $max_attempts ]; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ API is healthy!"
        break
    fi

    if [ $attempt -eq $max_attempts ]; then
        echo "⚠️  API health check failed, but services are running"
        break
    fi

    echo "   Attempt $attempt/$max_attempts - waiting for API..."
    sleep 3
    ((attempt++))
done

# 显示最近的日志
echo "📝 Showing recent logs..."
docker-compose logs --tail=10

echo ""
echo "🎉 EvoFlow services started successfully!"
echo ""
echo "📚 Available endpoints:"
echo "   • API Documentation: http://localhost:8000/docs"
echo "   • Health Check: http://localhost:8000/health"
echo "   • API Base URL: http://localhost:8000/api/v1"
echo ""
echo "👤 Default login credentials:"
echo "   • Email: admin@evoflow.ai"
echo "   • Password: secret"
echo ""
echo "🛠️  Useful commands:"
echo "   • View logs: docker-compose logs -f"
echo "   • Stop services: ./scripts/stop.sh"
echo "   • Restart: docker-compose restart"
