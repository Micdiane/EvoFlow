"""
工作流API路由
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession

from ...database import get_async_db
from ...models import Workflow, WorkflowExecution
from ...schemas.workflow import (
    WorkflowCreate, WorkflowUpdate, WorkflowResponse,
    WorkflowExecuteRequest, WorkflowExecuteResponse
)
from ...workflow.engine import WorkflowEngine

router = APIRouter()

# 全局工作流引擎实例
workflow_engine = WorkflowEngine()


@router.get("/", response_model=List[WorkflowResponse])
async def list_workflows(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_async_db)
):
    """获取工作流列表"""
    from sqlalchemy import select
    
    query = select(Workflow).offset(skip).limit(limit)
    result = await db.execute(query)
    workflows = result.scalars().all()
    
    return [WorkflowResponse.from_orm(workflow) for workflow in workflows]


@router.post("/", response_model=WorkflowResponse)
async def create_workflow(
    workflow: WorkflowCreate,
    db: AsyncSession = Depends(get_async_db)
):
    """创建工作流"""
    # TODO: 添加用户认证，获取当前用户ID
    user_id = "00000000-0000-0000-0000-000000000000"  # 临时用户ID
    
    db_workflow = Workflow(
        name=workflow.name,
        description=workflow.description,
        user_id=user_id,
        dag_definition=workflow.dag_definition,
        status="draft"
    )
    
    db.add(db_workflow)
    await db.commit()
    await db.refresh(db_workflow)
    
    return WorkflowResponse.from_orm(db_workflow)


@router.get("/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow(
    workflow_id: str,
    db: AsyncSession = Depends(get_async_db)
):
    """获取工作流详情"""
    workflow = await db.get(Workflow, workflow_id)
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found"
        )
    
    return WorkflowResponse.from_orm(workflow)


@router.put("/{workflow_id}", response_model=WorkflowResponse)
async def update_workflow(
    workflow_id: str,
    workflow_update: WorkflowUpdate,
    db: AsyncSession = Depends(get_async_db)
):
    """更新工作流"""
    workflow = await db.get(Workflow, workflow_id)
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found"
        )
    
    update_data = workflow_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(workflow, field, value)
    
    await db.commit()
    await db.refresh(workflow)
    
    return WorkflowResponse.from_orm(workflow)


@router.delete("/{workflow_id}")
async def delete_workflow(
    workflow_id: str,
    db: AsyncSession = Depends(get_async_db)
):
    """删除工作流"""
    workflow = await db.get(Workflow, workflow_id)
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found"
        )
    
    await db.delete(workflow)
    await db.commit()
    
    return {"message": "Workflow deleted successfully"}


@router.post("/{workflow_id}/execute", response_model=WorkflowExecuteResponse)
async def execute_workflow(
    workflow_id: str,
    execute_request: WorkflowExecuteRequest,
    db: AsyncSession = Depends(get_async_db)
):
    """执行工作流"""
    workflow = await db.get(Workflow, workflow_id)
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found"
        )
    
    if workflow.status != "active":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Workflow is not active"
        )
    
    try:
        execution_id = await workflow_engine.execute_workflow(
            workflow_id=workflow_id,
            dag_definition=workflow.dag_definition,
            input_data=execute_request.input_data,
            user_id=str(workflow.user_id)
        )
        
        return WorkflowExecuteResponse(
            execution_id=execution_id,
            status="running",
            message="Workflow execution started successfully"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start workflow execution: {str(e)}"
        )


@router.get("/{workflow_id}/executions")
async def list_workflow_executions(
    workflow_id: str,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_async_db)
):
    """获取工作流执行历史"""
    from sqlalchemy import select
    
    query = (
        select(WorkflowExecution)
        .where(WorkflowExecution.workflow_id == workflow_id)
        .offset(skip)
        .limit(limit)
        .order_by(WorkflowExecution.created_at.desc())
    )
    
    result = await db.execute(query)
    executions = result.scalars().all()
    
    return [
        {
            "id": str(execution.id),
            "status": execution.status,
            "started_at": execution.started_at.isoformat() if execution.started_at else None,
            "completed_at": execution.completed_at.isoformat() if execution.completed_at else None,
            "input_data": execution.input_data,
            "output_data": execution.output_data,
            "error_message": execution.error_message
        }
        for execution in executions
    ]
