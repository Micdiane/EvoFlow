"""
Agent基类定义
"""
import time
import uuid
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from decimal import Decimal

from loguru import logger


@dataclass
class AgentResult:
    """Agent执行结果"""
    success: bool
    data: Dict[str, Any]
    error_message: Optional[str] = None
    execution_time_ms: Optional[int] = None
    cost_estimate: Optional[Decimal] = None
    metadata: Optional[Dict[str, Any]] = None


class AgentError(Exception):
    """Agent执行异常"""
    pass


class BaseAgent(ABC):
    """Agent基类"""
    
    def __init__(
        self, 
        name: str, 
        agent_type: str,
        capabilities: List[str],
        config: Optional[Dict[str, Any]] = None
    ):
        self.id = str(uuid.uuid4())
        self.name = name
        self.agent_type = agent_type
        self.capabilities = capabilities
        self.config = config or {}
        
    @abstractmethod
    async def execute(self, input_data: Dict[str, Any], context: Dict[str, Any]) -> AgentResult:
        """
        执行Agent任务
        
        Args:
            input_data: 输入数据
            context: 执行上下文
            
        Returns:
            AgentResult: 执行结果
        """
        pass
    
    @abstractmethod
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """
        验证输入数据
        
        Args:
            input_data: 输入数据
            
        Returns:
            bool: 验证结果
        """
        pass
    
    @abstractmethod
    def get_cost_estimate(self, input_data: Dict[str, Any]) -> Decimal:
        """
        获取成本估算
        
        Args:
            input_data: 输入数据
            
        Returns:
            Decimal: 成本估算
        """
        pass
    
    async def run(self, input_data: Dict[str, Any], context: Dict[str, Any]) -> AgentResult:
        """
        运行Agent（包含时间统计和错误处理）
        
        Args:
            input_data: 输入数据
            context: 执行上下文
            
        Returns:
            AgentResult: 执行结果
        """
        start_time = time.time()
        
        try:
            # 验证输入
            if not self.validate_input(input_data):
                raise AgentError(f"Invalid input data for agent {self.name}")
            
            # 获取成本估算
            cost_estimate = self.get_cost_estimate(input_data)
            
            logger.info(f"Starting agent {self.name} execution")
            
            # 执行任务
            result = await self.execute(input_data, context)
            
            # 计算执行时间
            execution_time_ms = int((time.time() - start_time) * 1000)
            result.execution_time_ms = execution_time_ms
            result.cost_estimate = cost_estimate
            
            logger.info(f"Agent {self.name} completed in {execution_time_ms}ms")
            
            return result
            
        except Exception as e:
            execution_time_ms = int((time.time() - start_time) * 1000)
            error_message = str(e)
            
            logger.error(f"Agent {self.name} failed: {error_message}")
            
            return AgentResult(
                success=False,
                data={},
                error_message=error_message,
                execution_time_ms=execution_time_ms
            )
    
    def get_info(self) -> Dict[str, Any]:
        """获取Agent信息"""
        return {
            "id": self.id,
            "name": self.name,
            "type": self.agent_type,
            "capabilities": self.capabilities,
            "config": self.config
        }
