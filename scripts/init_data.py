#!/usr/bin/env python3
"""
初始化数据脚本
"""
import asyncio
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from evoflow.database import AsyncSessionLocal
from evoflow.models import User, Agent


async def create_default_user():
    """创建默认用户"""
    async with AsyncSessionLocal() as db:
        # 检查是否已存在默认用户
        from sqlalchemy import select
        result = await db.execute(select(User).where(User.email == "admin@evoflow.ai"))
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            print("默认用户已存在")
            return existing_user
        
        # 创建默认用户
        default_user = User(
            id=uuid.uuid4(),
            email="admin@evoflow.ai",
            username="admin",
            hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # "secret"
            is_active=True,
            is_superuser=True
        )
        
        db.add(default_user)
        await db.commit()
        await db.refresh(default_user)
        
        print(f"创建默认用户: {default_user.email}")
        return default_user


async def create_default_agents():
    """创建默认Agent"""
    async with AsyncSessionLocal() as db:
        agents_data = [
            {
                "name": "WebSearchAgent",
                "type": "web_search",
                "description": "网络搜索Agent，用于搜索互联网信息",
                "capabilities": ["web_search", "information_retrieval"],
                "config": {"max_results": 10, "timeout": 30}
            },
            {
                "name": "TextWritingAgent", 
                "type": "text_writing",
                "description": "文本生成Agent，基于DeepSeek API生成各种文本内容",
                "capabilities": ["text_generation", "creative_writing", "summarization"],
                "config": {"max_tokens": 2000, "temperature": 0.7, "model": "deepseek-chat"}
            },
            {
                "name": "DataAnalysisAgent",
                "type": "data_analysis", 
                "description": "数据分析Agent，用于分析和处理各种数据",
                "capabilities": ["data_analysis", "statistics", "visualization"],
                "config": {"max_data_size": "10MB"}
            },
            {
                "name": "EmailSenderAgent",
                "type": "email_sender",
                "description": "邮件发送Agent，用于发送邮件通知",
                "capabilities": ["email_sending", "notification"],
                "config": {"smtp_server": "smtp.gmail.com", "smtp_port": 587, "use_tls": True}
            },
            {
                "name": "FileProcessorAgent",
                "type": "file_processor",
                "description": "文件处理Agent，用于处理各种文件格式",
                "capabilities": ["file_processing", "format_conversion"],
                "config": {"supported_formats": ["txt", "csv", "json", "md"], "max_file_size": 10485760}
            }
        ]
        
        created_agents = []
        
        for agent_data in agents_data:
            # 检查Agent是否已存在
            from sqlalchemy import select
            result = await db.execute(
                select(Agent).where(Agent.name == agent_data["name"])
            )
            existing_agent = result.scalar_one_or_none()
            
            if existing_agent:
                print(f"Agent {agent_data['name']} 已存在")
                created_agents.append(existing_agent)
                continue
            
            # 创建新Agent
            agent = Agent(
                id=uuid.uuid4(),
                name=agent_data["name"],
                type=agent_data["type"],
                description=agent_data["description"],
                capabilities=agent_data["capabilities"],
                config=agent_data["config"],
                is_active=True
            )
            
            db.add(agent)
            created_agents.append(agent)
            print(f"创建Agent: {agent.name}")
        
        await db.commit()
        return created_agents


async def create_sample_workflow(user_id: str):
    """创建示例工作流"""
    from evoflow.models import Workflow
    
    async with AsyncSessionLocal() as db:
        # 检查是否已存在示例工作流
        from sqlalchemy import select
        result = await db.execute(
            select(Workflow).where(Workflow.name == "示例工作流：AI趋势分析")
        )
        existing_workflow = result.scalar_one_or_none()
        
        if existing_workflow:
            print("示例工作流已存在")
            return existing_workflow
        
        # 创建示例工作流DAG定义
        dag_definition = {
            "nodes": [
                {
                    "id": "search_node",
                    "name": "搜索AI最新信息",
                    "agent_type": "web_search",
                    "agent_config": {},
                    "input_data": {
                        "query": "人工智能最新发展趋势 2024",
                        "max_results": 5
                    },
                    "dependencies": [],
                    "conditions": {},
                    "max_retries": 3,
                    "timeout_seconds": 60
                },
                {
                    "id": "analyze_node",
                    "name": "分析搜索结果",
                    "agent_type": "text_writing",
                    "agent_config": {},
                    "input_data": {
                        "prompt": "请分析以下关于人工智能的搜索结果，总结主要的发展趋势：${dependency_search_node}",
                        "task_type": "summary",
                        "max_tokens": 1000,
                        "temperature": 0.7
                    },
                    "dependencies": ["search_node"],
                    "conditions": {},
                    "max_retries": 3,
                    "timeout_seconds": 120
                },
                {
                    "id": "report_node",
                    "name": "生成趋势报告",
                    "agent_type": "text_writing",
                    "agent_config": {},
                    "input_data": {
                        "prompt": "基于以下分析，生成一份专业的AI发展趋势报告，包括技术亮点、应用场景和未来展望：${dependency_analyze_node}",
                        "task_type": "business",
                        "max_tokens": 2000,
                        "temperature": 0.6
                    },
                    "dependencies": ["analyze_node"],
                    "conditions": {},
                    "max_retries": 3,
                    "timeout_seconds": 180
                }
            ]
        }
        
        # 创建工作流
        workflow = Workflow(
            id=uuid.uuid4(),
            name="示例工作流：AI趋势分析",
            description="这是一个示例工作流，展示如何使用EvoFlow进行AI趋势分析。包括网络搜索、内容分析和报告生成三个步骤。",
            user_id=user_id,
            dag_definition=dag_definition,
            status="active"
        )
        
        db.add(workflow)
        await db.commit()
        await db.refresh(workflow)
        
        print(f"创建示例工作流: {workflow.name}")
        return workflow


async def main():
    """主函数"""
    print("🚀 开始初始化EvoFlow数据...")
    
    try:
        # 创建默认用户
        print("\n1. 创建默认用户...")
        user = await create_default_user()
        
        # 创建默认Agent
        print("\n2. 创建默认Agent...")
        agents = await create_default_agents()
        
        # 创建示例工作流
        print("\n3. 创建示例工作流...")
        workflow = await create_sample_workflow(str(user.id))
        
        print("\n✅ 数据初始化完成！")
        print(f"   - 默认用户: {user.email}")
        print(f"   - 创建了 {len(agents)} 个Agent")
        print(f"   - 示例工作流: {workflow.name}")
        
        print("\n📝 登录信息:")
        print("   用户名: admin@evoflow.ai")
        print("   密码: secret")
        
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
