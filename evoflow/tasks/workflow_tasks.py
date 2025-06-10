"""
工作流相关的Celery任务
"""
from typing import Dict, Any
from celery import current_task

from ..celery_app import celery_app
from ..workflow.engine import WorkflowEngine


@celery_app.task(bind=True, name="evoflow.tasks.workflow.execute_workflow")
def execute_workflow_task(
    self,
    workflow_id: str,
    dag_definition: Dict[str, Any],
    input_data: Dict[str, Any] = None,
    user_id: str = None
):
    """
    异步执行工作流任务
    
    Args:
        workflow_id: 工作流ID
        dag_definition: DAG定义
        input_data: 输入数据
        user_id: 用户ID
    """
    try:
        # 更新任务状态
        self.update_state(
            state="PROGRESS",
            meta={"status": "Starting workflow execution"}
        )
        
        # 创建工作流引擎
        engine = WorkflowEngine()
        
        # 执行工作流（这里需要在异步环境中运行）
        import asyncio
        
        async def run_workflow():
            return await engine.execute_workflow(
                workflow_id=workflow_id,
                dag_definition=dag_definition,
                input_data=input_data or {},
                user_id=user_id
            )
        
        # 在新的事件循环中运行
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        execution_id = loop.run_until_complete(run_workflow())
        
        return {
            "status": "completed",
            "execution_id": execution_id,
            "workflow_id": workflow_id
        }
        
    except Exception as e:
        # 更新任务状态为失败
        self.update_state(
            state="FAILURE",
            meta={"error": str(e)}
        )
        raise


@celery_app.task(name="evoflow.tasks.workflow.cleanup_old_executions")
def cleanup_old_executions_task():
    """清理旧的执行记录"""
    try:
        # 这里可以实现清理逻辑
        # 例如删除超过30天的执行记录
        from datetime import datetime, timedelta
        from ..database import SessionLocal
        from ..models import WorkflowExecution
        
        cutoff_date = datetime.utcnow() - timedelta(days=30)
        
        with SessionLocal() as db:
            old_executions = db.query(WorkflowExecution).filter(
                WorkflowExecution.created_at < cutoff_date,
                WorkflowExecution.status.in_(["completed", "failed", "cancelled"])
            ).all()
            
            for execution in old_executions:
                db.delete(execution)
            
            db.commit()
            
            return {
                "status": "completed",
                "cleaned_count": len(old_executions)
            }
            
    except Exception as e:
        return {
            "status": "failed",
            "error": str(e)
        }
