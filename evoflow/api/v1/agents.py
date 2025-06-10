"""
Agent API路由
"""
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ...database import get_async_db
from ...models import Agent
from ...schemas.agent import AgentResponse, AgentCreate, AgentUpdate
from ...workflow.engine import WorkflowEngine

router = APIRouter()

# 全局工作流引擎实例
workflow_engine = WorkflowEngine()


@router.get("/", response_model=List[AgentResponse])
async def list_agents(
    skip: int = 0,
    limit: int = 100,
    agent_type: str = None,
    db: AsyncSession = Depends(get_async_db)
):
    """获取Agent列表"""
    from sqlalchemy import select
    
    query = select(Agent).offset(skip).limit(limit)
    
    if agent_type:
        query = query.where(Agent.type == agent_type)
    
    result = await db.execute(query)
    agents = result.scalars().all()
    
    return [AgentResponse.from_orm(agent) for agent in agents]


@router.get("/available")
async def get_available_agents():
    """获取所有可用的Agent类型和信息"""
    available_agents = workflow_engine.get_available_agents()
    
    return {
        "agents": available_agents,
        "total_count": len(available_agents)
    }


@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(
    agent_id: str,
    db: AsyncSession = Depends(get_async_db)
):
    """获取Agent详情"""
    agent = await db.get(Agent, agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    
    return AgentResponse.from_orm(agent)


@router.post("/", response_model=AgentResponse)
async def create_agent(
    agent: AgentCreate,
    db: AsyncSession = Depends(get_async_db)
):
    """创建自定义Agent"""
    db_agent = Agent(
        name=agent.name,
        type=agent.type,
        description=agent.description,
        capabilities=agent.capabilities,
        config=agent.config,
        is_active=True
    )
    
    db.add(db_agent)
    await db.commit()
    await db.refresh(db_agent)
    
    return AgentResponse.from_orm(db_agent)


@router.put("/{agent_id}", response_model=AgentResponse)
async def update_agent(
    agent_id: str,
    agent_update: AgentUpdate,
    db: AsyncSession = Depends(get_async_db)
):
    """更新Agent"""
    agent = await db.get(Agent, agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    
    update_data = agent_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(agent, field, value)
    
    await db.commit()
    await db.refresh(agent)
    
    return AgentResponse.from_orm(agent)


@router.delete("/{agent_id}")
async def delete_agent(
    agent_id: str,
    db: AsyncSession = Depends(get_async_db)
):
    """删除Agent"""
    agent = await db.get(Agent, agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    
    await db.delete(agent)
    await db.commit()
    
    return {"message": "Agent deleted successfully"}


@router.post("/{agent_id}/test")
async def test_agent(
    agent_id: str,
    test_data: Dict[str, Any],
    db: AsyncSession = Depends(get_async_db)
):
    """测试Agent功能"""
    agent = await db.get(Agent, agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    
    try:
        # 获取Agent实例
        agent_instance = workflow_engine.executor.get_agent(agent.type, agent.config)
        if not agent_instance:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Agent type {agent.type} not supported"
            )
        
        # 验证输入数据
        if not agent_instance.validate_input(test_data):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid input data for agent"
            )
        
        # 执行测试
        result = await agent_instance.run(test_data, {})
        
        return {
            "agent_id": agent_id,
            "agent_name": agent.name,
            "test_input": test_data,
            "test_result": {
                "success": result.success,
                "data": result.data,
                "error_message": result.error_message,
                "execution_time_ms": result.execution_time_ms,
                "cost_estimate": float(result.cost_estimate) if result.cost_estimate else None
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Agent test failed: {str(e)}"
        )
