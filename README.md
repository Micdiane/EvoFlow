### **项目名称：EvoFlow**

**副标题：** 一个自适应AI Agent工作流生成与优化平台

### **项目愿景 (Vision)**

创建一个智能平台，用户只需用自然语言描述一个复杂的目标（例如，“分析上个季度的销售数据，并生成一份面向高管的PPT报告”），EvoFlow 就能自动设计、编排和执行一个由多个专业AI Agent组成的工作流来完成任务。更核心的是，它能根据任务执行结果、成本、效率和用户反馈，不断地自我迭代和优化这个工作流，使其在未来处理相似任务时变得更高效、更智能、更经济。

### **核心理念 (Core Idea)**

传统的工作流自动化工具（如 Zapier, Make）或初级的 Agent 框架（如早期的 LangChain），需要用户手动定义每一步的流程和逻辑。EvoFlow 的核心突破在于 **“自动化生成”** 和 **“迭代优化”** 这两个环节，它将工作流本身视为一个需要被“进化”和“学习”的对象。

### **目标用户 (Target Users)**

1.  **业务分析师/运营人员：** 自动化处理数据分析、报告生成、市场监控等日常但复杂的任务。
2.  **内容创作者/市场营销团队：** 自动生成从选题、调研、文案撰写到多平台发布的全套内容流程。
3.  **软件开发者/DevOps工程师：** 自动化处理代码审查、Bug复现、测试用例生成、发布日志整理等流程。
4.  **研究人员：** 自动化进行文献检索、数据清洗、实验模拟、论文草稿撰写等科研工作。

### **核心功能模块**

#### 1. **意图理解与任务分解模块 (Intent & Decomposition Module)**

*   **输入：** 用户通过自然语言描述的高层级目标（e.g., "帮我策划一次线上新产品发布会"）。
*   **技术：** 使用强大的大型语言模型（LLM）如 GPT-4o 或 Claude 3 Opus，结合 RAG (Retrieval-Augmented Generation) 技术，理解用户意图的深层含义。
*   **输出：** 将高层级目标分解成一个逻辑上可行的、结构化的任务列表（Task Graph 的初步蓝图），例如：
    1.  确定目标受众。
    2.  研究竞品发布会策略。
    3.  制定宣传时间线。
    4.  撰写宣传文案和设计海报。
    5.  选择直播平台。
    6.  准备Q&A环节。

#### 2. **工作流自动生成模块 (Workflow Generation Module)**

*   **输入：** 任务分解后的结构化列表。
*   **核心：** 这是 **Planner Agent** 的主场。它像一个经验丰富的项目经理。
    *   **Agent/工具库 (Agent & Tool Library):** 系统内置一个可扩展的库，包含各种预定义的“原子Agent”（如 `WebSearchAgent`, `DataAnalysisAgent`, `CodeWriterAgent`, `EmailSenderAgent`）和“工具”（如 API 调用、数据库查询、文件读写）。
    *   **智能路由与编排：** Planner Agent 会为分解后的每个任务，从库中选择最合适的 Agent 或 Agent 组合来执行。它决定了任务是串行、并行还是有条件地执行，从而生成一个可视化的工作流图（DAG -有向无环图）。
*   **输出：** 一个可执行的、包含具体 Agent 和参数的完整工作流方案。

#### 3. **工作流执行引擎 (Workflow Execution Engine)**

*   **输入：** 生成的工作流方案（DAG）。
*   **功能：**
    *   **状态管理：** 跟踪每个 Agent 的执行状态（等待、运行中、成功、失败）。
    *   **上下文传递：** 管理和传递 Agent 之间的信息流（例如，`WebSearchAgent` 的研究结果需要传递给 `WritingAgent`）。
    *   **容错与重试：** 当某个 Agent 执行失败时，可以根据预设策略进行重试或触发备用方案。
    *   **人机协作（Human-in-the-Loop）：** 在关键决策点（如预算审批、文案终审）暂停工作流，并请求用户输入。

#### 4. **反馈与迭代优化模块 (Feedback & Optimization Module)**

这是 EvoFlow 的灵魂所在，让系统具备“成长”能力。

*   **输入：**
    *   **隐式反馈：** 任务执行的元数据（每个节点的耗时、Token成本、API调用成功率、最终任务的成功/失败状态）。
    *   **显式反馈：** 用户的直接评价（例如，对最终报告打分、点赞/点踩、提供修改意见 "这份报告的图表太少了"）。
*   **核心：** 这是 **Optimizer Agent** 或 **Reflector Agent** 的工作。
    *   **性能分析：** 分析哪些节点是瓶颈（耗时最长、成本最高），哪些 Agent 组合效率低下。
    *   **反馈学习：** 利用类似 RLHF (Reinforcement Learning from Human Feedback) 的机制，理解用户的偏好。例如，系统会学习到“对于这位用户，数据报告中必须包含至少3个可视化图表”。
    *   **策略演化：** 基于分析结果，优化工作流生成策略。这可能包括：
        *   **替换Agent：** "发现 `SimpleSearchAgent` 效果不佳，下次类似任务换成 `DeepResearchAgent`。"
        *   **调整流程：** "先写文案再配图的流程太慢，下次可以尝试并行处理。"
        *   **参数微调：** "对于创意写作，将 `WritingAgent` 的 `temperature` 参数调高一些。"
*   **输出：** 更新 Planner Agent 的决策模型或工作流模板库。当下次用户输入相似的目标时，系统会生成一个“进化”后的、更优的工作流。

### **技术架构简图**

```
+---------------------------------------------------------------------------------+
|                                  用户界面 (UI/CLI)                               |
+---------------------------------------------------------------------------------+
      | (1. 自然语言目标)
      V
+---------------------------------------------------------------------------------+
|                      意图理解与任务分解模块 (LLM + RAG)                          |
+---------------------------------------------------------------------------------+
      | (2. 结构化任务列表)
      V
+---------------------------------------------------------------------------------+
|                      工作流自动生成模块 (Planner Agent)                          |
|      [读取] -> [Agent/工具库]                                                    |
|      [受影响于] <-+ (6. 优化策略)                                                |
+-----------------|---------------------------------------------------------------+
                  | (3. 可执行工作流DAG)
                  V
+---------------------------------------------------------------------------------+
|                          工作流执行引擎 (Orchestrator)                           |
|      [调度] -> [Agent A] -> [Agent B] -> ...                                     |
|      [输出] -> (最终结果) -> 用户                                                |
+---------------------------------------------------------------------------------+
      | (4. 执行元数据)                                     ^ (5. 用户显式反馈)
      V                                                   |
+---------------------------------------------------------------------------------+
|                      反馈与迭代优化模块 (Optimizer Agent)                       |
|                             (分析 & 学习)                                        |
+---------------------------------------------------------------------------------+
```

### **项目实施路线图 (Roadmap)**

1.  **Phase 1 (MVP - 基础执行):**
    *   构建一个包含5-10个核心 Agent 的工具库。
    *   实现一个健壮的工作流执行引擎。
    *   用户需要手动（通过代码或简单的UI）定义工作流。
    *   **目标：** 验证 Agent 协同工作的可行性。

2.  **Phase 2 (自动化生成):**
    *   引入 Planner Agent，实现从自然语言到工作流的自动生成。
    *   重点攻关任务分解的准确性和 Agent 选择的合理性。
    *   **目标：** 实现 "零配置" 的任务完成能力。

3.  **Phase 3 (自我优化):**
    *   开发反馈与优化模块。
    *   首先基于执行元数据（成本、时间）进行初步的自动优化。
    *   引入简单的用户反馈机制（如打分）。
    *   **目标：** 让工作流具备初步的“自愈”和“提效”能力。

4.  **Phase 4 (生态与高级功能):**
    *   开放 Agent/工具库，允许社区开发者贡献自己的 Agent。
    *   引入更复杂的优化算法（如遗传算法来探索全新的工作流结构）。
    *   开发一个强大的可视化工作流编辑器，允许用户查看、修改和分享 EvoFlow 生成的工作流。
    *   **目标：** 打造一个开放、智能、不断进化的工作流自动化平台。

### **挑战与风险**

*   **可靠性与稳定性：** 动态生成的工作流可能出现意想不到的错误或死循环。
*   **成本控制：** 大量 LLM 和 API 调用可能导致成本失控，需要设计精巧的预算和监控机制。
*   **评估的复杂性：** 如何量化一个“好”的工作流？尤其是在创意性任务上，评价标准是模糊的。
*   **安全性：** Agent 如果能执行代码或操作文件，必须在严格的沙箱环境中运行，防止恶意行为。

这个 **EvoFlow** 项目构想不仅紧跟当前 AI Agent 的技术热点，而且通过引入“生成”和“优化”的闭环，解决了现有工具的核心痛点，具有巨大的技术深度和商业价值。

## **技术栈**

### **后端**
- **框架**: FastAPI (Python)
- **数据库**: PostgreSQL + Redis
- **LLM**: DeepSeek API
- **任务队列**: Celery
- **工作流引擎**: 自研DAG执行引擎

### **前端**
- **框架**: Next.js 14 (React)
- **UI**: Tailwind CSS + shadcn/ui
- **可视化**: React Flow
- **状态管理**: Zustand

### **开发环境**
- **容器化**: Docker + Docker Compose
- **包管理**: uv (Python)
- **数据库**: PostgreSQL 15
- **缓存**: Redis 7

## **快速开始**

### **环境要求**
- Python 3.11+
- Docker & Docker Compose
- uv (Python包管理器)

### **安装步骤**

1. **克隆项目**
```bash
git clone <repository-url>
cd EvoFlow
```

2. **配置环境变量**
```bash
cp .env.example .env
# 编辑.env文件，配置数据库和API密钥
```

3. **使用Docker启动（推荐）**
```bash
# 启动所有服务
chmod +x scripts/start.sh
./scripts/start.sh

# 或者使用docker-compose
docker-compose up -d
```

4. **开发环境启动**
```bash
# 启动开发环境
chmod +x scripts/dev.sh
./scripts/dev.sh
```

### **访问应用**
- API文档: http://localhost:8000/docs
- 健康检查: http://localhost:8000/health
- API接口: http://localhost:8000/api/v1

## **项目结构**

```
EvoFlow/
├── evoflow/                    # 主应用目录
│   ├── __init__.py
│   ├── main.py                 # FastAPI应用入口
│   ├── config.py               # 配置管理
│   ├── database.py             # 数据库配置
│   ├── celery_app.py           # Celery配置
│   ├── models/                 # 数据模型
│   │   ├── user.py
│   │   ├── workflow.py
│   │   ├── agent.py
│   │   └── task.py
│   ├── schemas/                # Pydantic模式
│   │   ├── workflow.py
│   │   └── agent.py
│   ├── api/                    # API路由
│   │   └── v1/
│   │       ├── workflows.py
│   │       ├── agents.py
│   │       └── executions.py
│   ├── agents/                 # Agent实现
│   │   ├── base.py
│   │   ├── web_search.py
│   │   ├── text_writing.py
│   │   ├── data_analysis.py
│   │   ├── email_sender.py
│   │   └── file_processor.py
│   ├── workflow/               # 工作流引擎
│   │   ├── dag.py
│   │   ├── engine.py
│   │   └── executor.py
│   ├── tasks/                  # Celery任务
│   │   ├── workflow_tasks.py
│   │   └── agent_tasks.py
│   └── utils/                  # 工具函数
│       ├── logger.py
│       └── validators.py
├── examples/                   # 示例代码
│   ├── simple_workflow.py
│   └── test_agents.py
├── scripts/                    # 启动脚本
│   ├── start.sh
│   ├── stop.sh
│   ├── dev.sh
│   └── init.sql
├── tests/                      # 测试文件
├── logs/                       # 日志目录
├── docker-compose.yml          # Docker编排
├── Dockerfile                  # Docker镜像
├── pyproject.toml              # Python项目配置
├── .env                        # 环境变量
└── README.md                   # 项目文档
```

## **核心功能**

### **1. Agent系统**
- **WebSearchAgent**: 网络搜索功能
- **TextWritingAgent**: 基于DeepSeek的文本生成
- **DataAnalysisAgent**: 数据分析和统计
- **EmailSenderAgent**: 邮件发送功能
- **FileProcessorAgent**: 文件处理和格式转换

### **2. 工作流引擎**
- **DAG构建**: 支持复杂的有向无环图工作流
- **并行执行**: 自动识别可并行执行的任务
- **错误处理**: 支持重试和容错机制
- **状态管理**: 实时跟踪执行状态
- **上下文传递**: 节点间数据流管理

### **3. API接口**
- **工作流管理**: 创建、更新、删除工作流
- **执行控制**: 启动、取消、监控执行
- **Agent管理**: 查看、测试、配置Agent
- **执行历史**: 查看执行记录和日志

## **使用示例**

### **创建简单工作流**

```python
from evoflow.workflow.dag import DAGNode, WorkflowDAG

# 创建节点
nodes = [
    DAGNode(
        id="search",
        name="搜索信息",
        agent_type="web_search",
        input_data={"query": "AI最新发展", "max_results": 5}
    ),
    DAGNode(
        id="analyze",
        name="分析结果",
        agent_type="text_writing",
        input_data={
            "prompt": "分析搜索结果: ${dependency_search}",
            "max_tokens": 1000
        },
        dependencies=["search"]
    )
]

# 创建并执行工作流
dag = WorkflowDAG(nodes)
engine = WorkflowEngine()
execution_id = await engine.execute_workflow("workflow_001", dag.to_dict())
```

### **测试Agent功能**

```python
from evoflow.agents import TextWritingAgent

agent = TextWritingAgent()
result = await agent.run({
    "prompt": "写一篇关于AI的文章",
    "max_tokens": 500
}, {})

print(f"生成结果: {result.data['generated_text']}")
```

## **API使用**

### **创建工作流**
```bash
curl -X POST "http://localhost:8000/api/v1/workflows/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "示例工作流",
    "description": "这是一个示例工作流",
    "dag_definition": {
      "nodes": [...]
    }
  }'
```

### **执行工作流**
```bash
curl -X POST "http://localhost:8000/api/v1/workflows/{workflow_id}/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "input_data": {"key": "value"}
  }'
```

### **查看执行状态**
```bash
curl "http://localhost:8000/api/v1/executions/{execution_id}"
```

## **开发指南**

### **添加新的Agent**

1. 继承BaseAgent类
2. 实现必需的方法
3. 在TaskExecutor中注册
4. 添加相应的测试

```python
class CustomAgent(BaseAgent):
    def __init__(self, config=None):
        super().__init__("CustomAgent", "custom", ["capability1"], config)

    async def execute(self, input_data, context):
        # 实现具体逻辑
        pass

    def validate_input(self, input_data):
        # 验证输入
        pass

    def get_cost_estimate(self, input_data):
        # 成本估算
        pass
```

### **运行测试**
```bash
# 安装测试依赖
uv pip install -e ".[dev]"

# 运行测试
pytest tests/

# 运行示例
python examples/test_agents.py
python examples/simple_workflow.py
```

## **部署**

### **生产环境部署**
1. 修改环境变量配置
2. 使用生产级数据库
3. 配置负载均衡
4. 设置监控和日志

### **Docker部署**
```bash
# 构建镜像
docker build -t evoflow:latest .

# 运行容器
docker-compose -f docker-compose.prod.yml up -d
```

## **贡献指南**

1. Fork项目
2. 创建功能分支
3. 提交更改
4. 创建Pull Request

## **许可证**

MIT License

## **项目状态**

### **✅ 已完成功能 (MVP Phase 1)**

**核心架构**
- [x] FastAPI后端框架搭建
- [x] PostgreSQL数据库设计和模型
- [x] Redis缓存和任务队列
- [x] Docker + uv开发环境
- [x] Alembic数据库迁移

**Agent系统**
- [x] BaseAgent抽象基类
- [x] WebSearchAgent - 网络搜索
- [x] TextWritingAgent - DeepSeek文本生成
- [x] DataAnalysisAgent - 数据分析
- [x] EmailSenderAgent - 邮件发送
- [x] FileProcessorAgent - 文件处理

**工作流引擎**
- [x] DAG有向无环图构建
- [x] 工作流执行引擎
- [x] 任务调度和状态管理
- [x] 错误处理和重试机制
- [x] 上下文数据传递

**API接口**
- [x] RESTful API设计
- [x] 工作流CRUD操作
- [x] Agent管理和测试
- [x] 执行监控和日志
- [x] 自动API文档生成

**开发工具**
- [x] 项目设置检查脚本
- [x] API测试脚本
- [x] 性能监控脚本
- [x] 数据初始化脚本

**部署支持**
- [x] Docker Compose开发环境
- [x] 生产环境Docker配置
- [x] Nginx反向代理配置
- [x] 自动化部署脚本

### **🚧 下一步计划 (Phase 2)**

**智能工作流生成**
- [ ] 自然语言任务分解
- [ ] Planner Agent实现
- [ ] Agent智能匹配算法
- [ ] 工作流模板库

**前端界面**
- [ ] Next.js前端项目初始化
- [ ] 工作流可视化编辑器
- [ ] 实时执行监控界面
- [ ] Agent管理界面

**用户系统**
- [ ] 用户认证和授权
- [ ] JWT Token管理
- [ ] 用户权限控制
- [ ] 多租户支持

**高级功能**
- [ ] 工作流版本控制
- [ ] 条件分支和循环
- [ ] 人机协作节点
- [ ] 工作流调试模式

### **🔮 未来规划 (Phase 3+)**

**优化与学习**
- [ ] 执行性能分析
- [ ] 用户反馈收集
- [ ] 强化学习优化
- [ ] 成本智能控制

**生态建设**
- [ ] Agent插件市场
- [ ] 社区贡献系统
- [ ] 工作流分享平台
- [ ] 第三方集成

**企业功能**
- [ ] 高级监控和告警
- [ ] 数据安全和合规
- [ ] 企业级部署方案
- [ ] 专业技术支持

## **快速验证**

### **1. 环境检查**
```bash
# 检查项目设置
python scripts/check_setup.py

# 或者给脚本执行权限
chmod +x scripts/check_setup.py
./scripts/check_setup.py
```

### **2. 启动服务**
```bash
# 开发环境启动
chmod +x scripts/start.sh
./scripts/start.sh

# 或者手动启动
docker-compose up -d
```

### **3. API测试**
```bash
# 运行API测试
python scripts/test_api.py

# 或者手动测试
curl http://localhost:8000/health
curl http://localhost:8000/docs
```

### **4. 性能监控**
```bash
# 运行监控脚本
python scripts/monitor.py

# 持续监控
python scripts/monitor.py --interval 30
```

## **故障排除**

### **常见问题**

**1. Docker服务启动失败**
```bash
# 检查Docker状态
docker info

# 查看服务日志
docker-compose logs

# 重启服务
docker-compose restart
```

**2. 数据库连接失败**
```bash
# 检查数据库状态
docker-compose exec postgres pg_isready -U evoflow

# 查看数据库日志
docker-compose logs postgres
```

**3. API响应慢或超时**
```bash
# 检查系统资源
python scripts/monitor.py --once

# 查看API日志
docker-compose logs backend
```

**4. Agent执行失败**
- 检查DeepSeek API密钥是否正确
- 确认网络连接正常
- 查看具体错误信息

### **日志查看**
```bash
# 查看所有服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f backend
docker-compose logs -f celery_worker

# 查看应用日志文件
tail -f logs/evoflow.log
```

## **贡献指南**

### **开发流程**
1. Fork项目到个人仓库
2. 创建功能分支: `git checkout -b feature/new-feature`
3. 提交更改: `git commit -am 'Add new feature'`
4. 推送分支: `git push origin feature/new-feature`
5. 创建Pull Request

### **代码规范**
- 使用Black进行代码格式化
- 遵循PEP 8编码规范
- 添加类型注解
- 编写单元测试
- 更新文档

### **测试要求**
```bash
# 运行测试
pytest tests/

# 代码格式检查
black --check evoflow/
isort --check-only evoflow/

# 类型检查
mypy evoflow/
```

## **许可证**

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## **致谢**

感谢以下开源项目和技术：
- FastAPI - 现代高性能Web框架
- SQLAlchemy - Python SQL工具包
- Celery - 分布式任务队列
- Redis - 内存数据结构存储
- PostgreSQL - 开源关系型数据库
- Docker - 容器化平台
- DeepSeek - 大语言模型API

## **联系方式**

- 项目地址: [GitHub Repository]
- 问题反馈: [Issues]
- 邮箱: team@evoflow.ai
- 文档: [Documentation]

---

**EvoFlow** - 让AI工作流自动化变得简单而强大 🚀
