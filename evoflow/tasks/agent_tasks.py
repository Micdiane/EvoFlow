"""
Agent相关的Celery任务
"""
from typing import Dict, Any

from ..celery_app import celery_app
from ..agents import BaseAgent


@celery_app.task(bind=True, name="evoflow.tasks.agent.execute_agent")
def execute_agent_task(
    self,
    agent_type: str,
    agent_config: Dict[str, Any],
    input_data: Dict[str, Any],
    context: Dict[str, Any] = None
):
    """
    异步执行Agent任务
    
    Args:
        agent_type: Agent类型
        agent_config: Agent配置
        input_data: 输入数据
        context: 执行上下文
    """
    try:
        # 更新任务状态
        self.update_state(
            state="PROGRESS",
            meta={"status": f"Executing {agent_type} agent"}
        )
        
        # 动态导入Agent类
        from ..workflow.executor import TaskExecutor
        
        executor = TaskExecutor()
        agent = executor.get_agent(agent_type, agent_config)
        
        if not agent:
            raise ValueError(f"Unknown agent type: {agent_type}")
        
        # 执行Agent（这里需要在异步环境中运行）
        import asyncio
        
        async def run_agent():
            return await agent.run(input_data, context or {})
        
        # 在新的事件循环中运行
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        result = loop.run_until_complete(run_agent())
        
        return {
            "status": "completed",
            "agent_type": agent_type,
            "success": result.success,
            "data": result.data,
            "error_message": result.error_message,
            "execution_time_ms": result.execution_time_ms,
            "cost_estimate": float(result.cost_estimate) if result.cost_estimate else None
        }
        
    except Exception as e:
        # 更新任务状态为失败
        self.update_state(
            state="FAILURE",
            meta={"error": str(e)}
        )
        raise


@celery_app.task(name="evoflow.tasks.agent.batch_execute_agents")
def batch_execute_agents_task(agent_tasks: list):
    """
    批量执行Agent任务
    
    Args:
        agent_tasks: Agent任务列表
    """
    results = []
    
    for task in agent_tasks:
        try:
            result = execute_agent_task.delay(
                agent_type=task["agent_type"],
                agent_config=task.get("agent_config", {}),
                input_data=task["input_data"],
                context=task.get("context", {})
            )
            
            results.append({
                "task_id": result.id,
                "agent_type": task["agent_type"],
                "status": "submitted"
            })
            
        except Exception as e:
            results.append({
                "agent_type": task["agent_type"],
                "status": "failed",
                "error": str(e)
            })
    
    return {
        "status": "completed",
        "total_tasks": len(agent_tasks),
        "results": results
    }
