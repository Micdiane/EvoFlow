"""
Agent相关的Pydantic模式
"""
from typing import Dict, Any, Optional, List
from datetime import datetime
from pydantic import BaseModel, Field
from uuid import UUID


class AgentBase(BaseModel):
    """Agent基础模式"""
    name: str = Field(..., description="Agent名称")
    type: str = Field(..., description="Agent类型")
    description: Optional[str] = Field(None, description="Agent描述")


class AgentCreate(AgentBase):
    """创建Agent模式"""
    capabilities: List[str] = Field(default_factory=list, description="Agent能力列表")
    config: Dict[str, Any] = Field(default_factory=dict, description="Agent配置")


class AgentUpdate(BaseModel):
    """更新Agent模式"""
    name: Optional[str] = Field(None, description="Agent名称")
    description: Optional[str] = Field(None, description="Agent描述")
    capabilities: Optional[List[str]] = Field(None, description="Agent能力列表")
    config: Optional[Dict[str, Any]] = Field(None, description="Agent配置")
    is_active: Optional[bool] = Field(None, description="是否激活")


class AgentResponse(AgentBase):
    """Agent响应模式"""
    id: UUID
    capabilities: List[str]
    config: Dict[str, Any]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class AgentTestRequest(BaseModel):
    """Agent测试请求模式"""
    input_data: Dict[str, Any] = Field(..., description="测试输入数据")


class AgentTestResponse(BaseModel):
    """Agent测试响应模式"""
    agent_id: str = Field(..., description="Agent ID")
    agent_name: str = Field(..., description="Agent名称")
    test_input: Dict[str, Any] = Field(..., description="测试输入")
    test_result: Dict[str, Any] = Field(..., description="测试结果")
