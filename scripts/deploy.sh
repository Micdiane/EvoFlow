#!/bin/bash

# EvoFlow 生产环境部署脚本

set -e  # 遇到错误立即退出

echo "🚀 开始部署EvoFlow到生产环境..."

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查必需的环境变量
check_env_vars() {
    log_info "检查环境变量..."
    
    required_vars=(
        "POSTGRES_PASSWORD"
        "REDIS_PASSWORD"
        "DEEPSEEK_API_KEY"
        "SECRET_KEY"
        "JWT_SECRET_KEY"
    )
    
    missing_vars=()
    
    for var in "${required_vars[@]}"; do
        if [ -z "${!var}" ]; then
            missing_vars+=("$var")
        fi
    done
    
    if [ ${#missing_vars[@]} -ne 0 ]; then
        log_error "缺少必需的环境变量:"
        for var in "${missing_vars[@]}"; do
            echo "  - $var"
        done
        echo ""
        echo "请在.env.prod文件中设置这些变量，或者通过环境变量传递"
        exit 1
    fi
    
    log_success "环境变量检查通过"
}

# 检查Docker和Docker Compose
check_docker() {
    log_info "检查Docker环境..."
    
    if ! command -v docker &> /dev/null; then
        log_error "Docker未安装"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose未安装"
        exit 1
    fi
    
    if ! docker info > /dev/null 2>&1; then
        log_error "Docker服务未运行"
        exit 1
    fi
    
    log_success "Docker环境检查通过"
}

# 创建必要的目录
create_directories() {
    log_info "创建必要的目录..."
    
    directories=(
        "logs"
        "logs/nginx"
        "backups"
        "uploads"
        "nginx/ssl"
        "monitoring"
        "monitoring/grafana/dashboards"
        "monitoring/grafana/datasources"
    )
    
    for dir in "${directories[@]}"; do
        mkdir -p "$dir"
        log_info "创建目录: $dir"
    done
    
    log_success "目录创建完成"
}

# 备份现有数据
backup_data() {
    if [ "$1" = "--skip-backup" ]; then
        log_warning "跳过数据备份"
        return
    fi
    
    log_info "备份现有数据..."
    
    timestamp=$(date +"%Y%m%d_%H%M%S")
    backup_dir="backups/backup_$timestamp"
    
    mkdir -p "$backup_dir"
    
    # 备份数据库（如果存在）
    if docker ps | grep -q evoflow_postgres; then
        log_info "备份PostgreSQL数据库..."
        docker exec evoflow_postgres pg_dump -U evoflow evoflow > "$backup_dir/database.sql"
        log_success "数据库备份完成: $backup_dir/database.sql"
    fi
    
    # 备份配置文件
    if [ -f ".env" ]; then
        cp .env "$backup_dir/env_backup"
        log_info "环境配置备份完成"
    fi
    
    log_success "数据备份完成: $backup_dir"
}

# 构建Docker镜像
build_images() {
    log_info "构建Docker镜像..."
    
    # 构建生产环境镜像
    docker-compose -f docker-compose.prod.yml build --no-cache
    
    log_success "Docker镜像构建完成"
}

# 部署服务
deploy_services() {
    log_info "部署服务..."
    
    # 停止现有服务
    log_info "停止现有服务..."
    docker-compose -f docker-compose.prod.yml down
    
    # 启动数据库和Redis
    log_info "启动数据库和Redis..."
    docker-compose -f docker-compose.prod.yml up -d postgres redis
    
    # 等待数据库启动
    log_info "等待数据库启动..."
    max_attempts=30
    attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if docker-compose -f docker-compose.prod.yml exec -T postgres pg_isready -U evoflow > /dev/null 2>&1; then
            log_success "数据库已就绪"
            break
        fi
        
        if [ $attempt -eq $max_attempts ]; then
            log_error "数据库启动超时"
            exit 1
        fi
        
        log_info "等待数据库启动... ($attempt/$max_attempts)"
        sleep 2
        ((attempt++))
    done
    
    # 运行数据库迁移
    log_info "运行数据库迁移..."
    docker-compose -f docker-compose.prod.yml run --rm backend alembic upgrade head
    
    # 初始化数据
    log_info "初始化数据..."
    docker-compose -f docker-compose.prod.yml run --rm backend python scripts/init_data.py
    
    # 启动所有服务
    log_info "启动所有服务..."
    docker-compose -f docker-compose.prod.yml up -d
    
    log_success "服务部署完成"
}

# 健康检查
health_check() {
    log_info "执行健康检查..."
    
    max_attempts=20
    attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s http://localhost/health > /dev/null 2>&1; then
            log_success "健康检查通过"
            return 0
        fi
        
        if [ $attempt -eq $max_attempts ]; then
            log_error "健康检查失败"
            return 1
        fi
        
        log_info "健康检查... ($attempt/$max_attempts)"
        sleep 5
        ((attempt++))
    done
}

# 显示部署信息
show_deployment_info() {
    log_success "🎉 EvoFlow部署完成！"
    echo ""
    echo "📚 服务访问地址:"
    echo "  • API文档: http://localhost/docs"
    echo "  • 健康检查: http://localhost/health"
    echo "  • API接口: http://localhost/api/v1"
    echo "  • Flower监控: http://localhost:5555"
    echo "  • Grafana监控: http://localhost:3000"
    echo "  • Prometheus: http://localhost:9090"
    echo ""
    echo "👤 默认登录信息:"
    echo "  • 管理员邮箱: admin@evoflow.ai"
    echo "  • 管理员密码: secret"
    echo ""
    echo "🛠️  管理命令:"
    echo "  • 查看日志: docker-compose -f docker-compose.prod.yml logs -f"
    echo "  • 重启服务: docker-compose -f docker-compose.prod.yml restart"
    echo "  • 停止服务: docker-compose -f docker-compose.prod.yml down"
    echo "  • 查看状态: docker-compose -f docker-compose.prod.yml ps"
    echo ""
}

# 清理函数
cleanup() {
    if [ $? -ne 0 ]; then
        log_error "部署失败，正在清理..."
        docker-compose -f docker-compose.prod.yml down
    fi
}

# 主函数
main() {
    # 设置错误处理
    trap cleanup EXIT
    
    # 解析命令行参数
    SKIP_BACKUP=false
    SKIP_BUILD=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --skip-backup)
                SKIP_BACKUP=true
                shift
                ;;
            --skip-build)
                SKIP_BUILD=true
                shift
                ;;
            --help)
                echo "用法: $0 [选项]"
                echo ""
                echo "选项:"
                echo "  --skip-backup    跳过数据备份"
                echo "  --skip-build     跳过镜像构建"
                echo "  --help           显示帮助信息"
                exit 0
                ;;
            *)
                log_error "未知选项: $1"
                exit 1
                ;;
        esac
    done
    
    # 加载环境变量
    if [ -f ".env.prod" ]; then
        log_info "加载生产环境配置..."
        export $(cat .env.prod | grep -v '^#' | xargs)
    elif [ -f ".env" ]; then
        log_warning "使用开发环境配置，建议创建.env.prod文件"
        export $(cat .env | grep -v '^#' | xargs)
    else
        log_error "未找到环境配置文件"
        exit 1
    fi
    
    # 执行部署步骤
    check_env_vars
    check_docker
    create_directories
    
    if [ "$SKIP_BACKUP" = false ]; then
        backup_data
    else
        backup_data --skip-backup
    fi
    
    if [ "$SKIP_BUILD" = false ]; then
        build_images
    fi
    
    deploy_services
    
    # 等待服务启动
    sleep 10
    
    if health_check; then
        show_deployment_info
    else
        log_error "部署验证失败，请检查日志"
        docker-compose -f docker-compose.prod.yml logs --tail=50
        exit 1
    fi
}

# 运行主函数
main "$@"
