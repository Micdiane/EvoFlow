"""
任务执行模型
"""
import uuid
from datetime import datetime
from decimal import Decimal
from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey, JSON, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from ..database import Base


class TaskExecution(Base):
    """任务执行记录模型"""
    
    __tablename__ = "task_executions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workflow_execution_id = Column(UUID(as_uuid=True), ForeignKey("workflow_executions.id"), nullable=False)
    agent_id = Column(UUID(as_uuid=True), ForeignKey("agents.id"), nullable=False)
    task_name = Column(String(255), nullable=False)
    status = Column(String(50), default="pending")  # pending, running, completed, failed, skipped
    input_data = Column(JSON)  # 任务输入数据
    output_data = Column(JSON)  # 任务输出数据
    error_message = Column(Text)  # 错误信息
    execution_time_ms = Column(Integer)  # 执行时间（毫秒）
    cost_estimate = Column(Numeric(10, 4))  # 成本估算
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关系
    workflow_execution = relationship("WorkflowExecution", back_populates="task_executions")
    agent = relationship("Agent", back_populates="task_executions")
    
    @property
    def duration_seconds(self):
        """执行时长（秒）"""
        if self.execution_time_ms:
            return self.execution_time_ms / 1000.0
        return None
    
    def __repr__(self):
        return f"<TaskExecution(id={self.id}, task_name={self.task_name}, status={self.status})>"
