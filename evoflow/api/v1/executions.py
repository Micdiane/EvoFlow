"""
执行API路由
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ...database import get_async_db
from ...models import WorkflowExecution, TaskExecution
from ...workflow.engine import WorkflowEngine

router = APIRouter()

# 全局工作流引擎实例
workflow_engine = WorkflowEngine()


@router.get("/{execution_id}")
async def get_execution_status(
    execution_id: str,
    db: AsyncSession = Depends(get_async_db)
):
    """获取执行状态"""
    execution_status = await workflow_engine.get_execution_status(execution_id)
    
    if not execution_status:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Execution not found"
        )
    
    return execution_status


@router.post("/{execution_id}/cancel")
async def cancel_execution(
    execution_id: str,
    db: AsyncSession = Depends(get_async_db)
):
    """取消执行"""
    success = await workflow_engine.cancel_workflow(execution_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Execution not found or already completed"
        )
    
    return {"message": "Execution cancelled successfully"}


@router.get("/{execution_id}/tasks")
async def get_execution_tasks(
    execution_id: str,
    db: AsyncSession = Depends(get_async_db)
):
    """获取执行的任务列表"""
    from sqlalchemy import select
    
    # 验证执行是否存在
    execution = await db.get(WorkflowExecution, execution_id)
    if not execution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Execution not found"
        )
    
    # 获取任务列表
    query = (
        select(TaskExecution)
        .where(TaskExecution.workflow_execution_id == execution_id)
        .order_by(TaskExecution.created_at)
    )
    
    result = await db.execute(query)
    tasks = result.scalars().all()
    
    return [
        {
            "id": str(task.id),
            "task_name": task.task_name,
            "agent_id": str(task.agent_id) if task.agent_id else None,
            "status": task.status,
            "input_data": task.input_data,
            "output_data": task.output_data,
            "error_message": task.error_message,
            "execution_time_ms": task.execution_time_ms,
            "cost_estimate": float(task.cost_estimate) if task.cost_estimate else None,
            "started_at": task.started_at.isoformat() if task.started_at else None,
            "completed_at": task.completed_at.isoformat() if task.completed_at else None,
            "created_at": task.created_at.isoformat()
        }
        for task in tasks
    ]


@router.get("/{execution_id}/logs")
async def get_execution_logs(
    execution_id: str,
    db: AsyncSession = Depends(get_async_db)
):
    """获取执行日志"""
    # 验证执行是否存在
    execution = await db.get(WorkflowExecution, execution_id)
    if not execution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Execution not found"
        )
    
    # 这里可以集成日志系统，返回详细的执行日志
    # 目前返回基本信息
    return {
        "execution_id": execution_id,
        "logs": [
            {
                "timestamp": execution.created_at.isoformat(),
                "level": "INFO",
                "message": f"Workflow execution {execution_id} created"
            },
            {
                "timestamp": execution.started_at.isoformat() if execution.started_at else None,
                "level": "INFO", 
                "message": f"Workflow execution {execution_id} started"
            }
        ]
    }


@router.get("/")
async def list_executions(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    workflow_id: Optional[str] = None,
    db: AsyncSession = Depends(get_async_db)
):
    """获取执行列表"""
    from sqlalchemy import select
    
    query = select(WorkflowExecution).offset(skip).limit(limit)
    
    if status:
        query = query.where(WorkflowExecution.status == status)
    
    if workflow_id:
        query = query.where(WorkflowExecution.workflow_id == workflow_id)
    
    query = query.order_by(WorkflowExecution.created_at.desc())
    
    result = await db.execute(query)
    executions = result.scalars().all()
    
    return [
        {
            "id": str(execution.id),
            "workflow_id": str(execution.workflow_id),
            "status": execution.status,
            "started_at": execution.started_at.isoformat() if execution.started_at else None,
            "completed_at": execution.completed_at.isoformat() if execution.completed_at else None,
            "duration": execution.duration,
            "input_data": execution.input_data,
            "output_data": execution.output_data,
            "error_message": execution.error_message,
            "created_at": execution.created_at.isoformat()
        }
        for execution in executions
    ]
