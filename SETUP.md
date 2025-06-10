# EvoFlow 项目设置指南

## 🚀 快速开始

### 1. 环境准备

**必需软件:**
- Python 3.11+
- Docker Desktop
- Git

**推荐工具:**
- VS Code
- Postman (API测试)

### 2. 项目初始化

```bash
# 克隆项目
git clone <repository-url>
cd EvoFlow

# 安装uv包管理器
pip install uv

# 创建虚拟环境
uv venv

# 激活虚拟环境 (Windows)
.venv\Scripts\activate

# 激活虚拟环境 (Linux/Mac)
source .venv/bin/activate

# 安装依赖
uv pip install -e ".[dev]"
```

### 3. 环境配置

```bash
# 复制环境变量文件
cp .env.example .env

# 编辑.env文件，设置必要的配置
# 特别是DEEPSEEK_API_KEY
```

### 4. 启动服务

**Windows用户:**
```powershell
# 启动Docker Desktop

# 启动服务
docker-compose up -d

# 等待服务启动后，运行数据库迁移
docker-compose exec backend alembic upgrade head

# 初始化数据
docker-compose exec backend python scripts/init_data.py
```

**Linux/Mac用户:**
```bash
# 给脚本执行权限
chmod +x scripts/*.sh

# 启动服务
./scripts/start.sh
```

### 5. 验证安装

```bash
# 检查项目设置
python scripts/check_setup.py

# 验证项目完整性
python scripts/validate_project.py

# 测试API
python scripts/test_api.py

# 访问API文档
# http://localhost:8000/docs
```

## 🔧 开发环境设置

### IDE配置 (VS Code)

推荐安装的扩展:
- Python
- Docker
- REST Client
- GitLens

**settings.json配置:**
```json
{
    "python.defaultInterpreterPath": ".venv/bin/python",
    "python.formatting.provider": "black",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": false,
    "python.linting.flake8Enabled": true,
    "editor.formatOnSave": true
}
```

### 代码质量工具

```bash
# 代码格式化
black evoflow/

# 导入排序
isort evoflow/

# 代码检查
flake8 evoflow/

# 类型检查
mypy evoflow/

# 运行测试
pytest tests/
```

## 🐳 Docker 使用指南

### 开发环境

```bash
# 启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down

# 重启特定服务
docker-compose restart backend
```

### 生产环境

```bash
# 构建生产镜像
docker-compose -f docker-compose.prod.yml build

# 启动生产环境
docker-compose -f docker-compose.prod.yml up -d

# 或使用部署脚本
./scripts/deploy.sh
```

## 📊 监控和调试

### 日志查看

```bash
# 应用日志
tail -f logs/evoflow.log

# Docker日志
docker-compose logs -f backend
docker-compose logs -f celery_worker

# 数据库日志
docker-compose logs -f postgres
```

### 性能监控

```bash
# 一次性监控
python scripts/monitor.py --once

# 持续监控
python scripts/monitor.py --interval 30

# 访问监控界面
# Flower: http://localhost:5555
# Grafana: http://localhost:3000 (生产环境)
```

### 调试技巧

1. **API调试:**
   - 使用 http://localhost:8000/docs 进行交互式测试
   - 查看详细的错误信息和堆栈跟踪

2. **数据库调试:**
   ```bash
   # 连接数据库
   docker-compose exec postgres psql -U evoflow -d evoflow
   
   # 查看表结构
   \dt
   \d users
   ```

3. **Celery调试:**
   ```bash
   # 查看任务状态
   docker-compose exec celery_worker celery -A evoflow.celery_app inspect active
   
   # 查看队列状态
   docker-compose exec celery_worker celery -A evoflow.celery_app inspect stats
   ```

## 🧪 测试指南

### 运行测试

```bash
# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/test_basic.py

# 运行带覆盖率的测试
pytest --cov=evoflow

# 生成HTML覆盖率报告
pytest --cov=evoflow --cov-report=html
```

### API测试

```bash
# 自动化API测试
python scripts/test_api.py

# 手动测试示例
curl -X GET "http://localhost:8000/health"
curl -X GET "http://localhost:8000/api/v1/agents/"
```

### Agent测试

```bash
# 运行Agent示例
python examples/test_agents.py

# 运行工作流示例
python examples/simple_workflow.py
```

## 🚀 部署指南

### 开发部署

```bash
# 使用开发配置
docker-compose up -d
```

### 生产部署

```bash
# 创建生产环境配置
cp .env.example .env.prod
# 编辑.env.prod，设置生产环境变量

# 运行部署脚本
./scripts/deploy.sh

# 或手动部署
docker-compose -f docker-compose.prod.yml up -d
```

### 环境变量配置

**开发环境 (.env):**
```env
DEBUG=true
LOG_LEVEL=DEBUG
DATABASE_URL=postgresql://evoflow:evoflow_password@localhost:5432/evoflow
```

**生产环境 (.env.prod):**
```env
DEBUG=false
LOG_LEVEL=INFO
DATABASE_URL=postgresql://user:password@prod-db:5432/evoflow
SECRET_KEY=your-production-secret-key
```

## 🔒 安全注意事项

1. **API密钥管理:**
   - 不要在代码中硬编码API密钥
   - 使用环境变量或密钥管理服务
   - 定期轮换密钥

2. **数据库安全:**
   - 使用强密码
   - 限制数据库访问权限
   - 定期备份数据

3. **网络安全:**
   - 在生产环境中使用HTTPS
   - 配置防火墙规则
   - 使用反向代理

## 🆘 故障排除

### 常见问题

**1. 端口冲突**
```bash
# 查看端口占用
netstat -ano | findstr :8000  # Windows
lsof -i :8000                 # Linux/Mac

# 修改端口配置
# 编辑docker-compose.yml中的端口映射
```

**2. 内存不足**
```bash
# 检查Docker资源限制
docker system df
docker system prune

# 增加Docker内存限制
# Docker Desktop -> Settings -> Resources
```

**3. 数据库连接失败**
```bash
# 检查数据库状态
docker-compose exec postgres pg_isready -U evoflow

# 重置数据库
docker-compose down -v
docker-compose up -d postgres
```

**4. 依赖安装失败**
```bash
# 清理缓存
uv cache clean

# 重新安装
uv pip install -e ".[dev]" --force-reinstall
```

### 获取帮助

1. 查看项目文档和README
2. 运行诊断脚本: `python scripts/check_setup.py`
3. 查看日志文件获取详细错误信息
4. 在GitHub Issues中搜索相似问题
5. 提交新的Issue并提供详细信息

## 📚 相关资源

- [FastAPI文档](https://fastapi.tiangolo.com/)
- [SQLAlchemy文档](https://docs.sqlalchemy.org/)
- [Celery文档](https://docs.celeryproject.org/)
- [Docker文档](https://docs.docker.com/)
- [DeepSeek API文档](https://platform.deepseek.com/api-docs/)

---

如有问题，请参考故障排除部分或提交Issue。
