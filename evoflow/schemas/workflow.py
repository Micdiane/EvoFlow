"""
工作流相关的Pydantic模式
"""
from typing import Dict, Any, Optional, List
from datetime import datetime
from pydantic import BaseModel, Field
from uuid import UUID


class WorkflowBase(BaseModel):
    """工作流基础模式"""
    name: str = Field(..., description="工作流名称")
    description: Optional[str] = Field(None, description="工作流描述")


class WorkflowCreate(WorkflowBase):
    """创建工作流模式"""
    dag_definition: Dict[str, Any] = Field(..., description="DAG定义")


class WorkflowUpdate(BaseModel):
    """更新工作流模式"""
    name: Optional[str] = Field(None, description="工作流名称")
    description: Optional[str] = Field(None, description="工作流描述")
    dag_definition: Optional[Dict[str, Any]] = Field(None, description="DAG定义")
    status: Optional[str] = Field(None, description="工作流状态")


class WorkflowResponse(WorkflowBase):
    """工作流响应模式"""
    id: UUID
    user_id: UUID
    dag_definition: Dict[str, Any]
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class WorkflowExecuteRequest(BaseModel):
    """工作流执行请求模式"""
    input_data: Dict[str, Any] = Field(default_factory=dict, description="输入数据")


class WorkflowExecuteResponse(BaseModel):
    """工作流执行响应模式"""
    execution_id: str = Field(..., description="执行ID")
    status: str = Field(..., description="执行状态")
    message: str = Field(..., description="响应消息")


class DAGNodeSchema(BaseModel):
    """DAG节点模式"""
    id: str = Field(..., description="节点ID")
    name: str = Field(..., description="节点名称")
    agent_type: str = Field(..., description="Agent类型")
    agent_config: Dict[str, Any] = Field(default_factory=dict, description="Agent配置")
    input_data: Dict[str, Any] = Field(default_factory=dict, description="输入数据")
    dependencies: List[str] = Field(default_factory=list, description="依赖节点")
    conditions: Dict[str, Any] = Field(default_factory=dict, description="执行条件")
    max_retries: int = Field(default=3, description="最大重试次数")
    timeout_seconds: int = Field(default=300, description="超时时间（秒）")


class WorkflowDAGSchema(BaseModel):
    """工作流DAG模式"""
    nodes: List[DAGNodeSchema] = Field(..., description="节点列表")
