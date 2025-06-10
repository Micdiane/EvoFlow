"""
任务执行器
"""
import asyncio
import time
from typing import Dict, Any, Optional
from datetime import datetime

from loguru import logger

from .dag import DAGNode, NodeStatus
from ..agents import (
    BaseAgent, WebSearchAgent, TextWritingAgent, 
    DataAnalysisAgent, EmailSenderAgent, FileProcessorAgent
)


class TaskExecutor:
    """任务执行器"""
    
    def __init__(self):
        self.agent_registry = self._initialize_agents()
    
    def _initialize_agents(self) -> Dict[str, BaseAgent]:
        """初始化Agent注册表"""
        agents = {}
        
        # 注册所有可用的Agent
        agents["web_search"] = WebSearchAgent()
        agents["text_writing"] = TextWritingAgent()
        agents["data_analysis"] = DataAnalysisAgent()
        agents["email_sender"] = EmailSenderAgent()
        agents["file_processor"] = FileProcessorAgent()
        
        return agents
    
    def get_agent(self, agent_type: str, config: Dict[str, Any] = None) -> Optional[BaseAgent]:
        """获取Agent实例"""
        if agent_type not in self.agent_registry:
            logger.error(f"Unknown agent type: {agent_type}")
            return None
        
        # 如果有自定义配置，创建新的Agent实例
        if config:
            agent_class = type(self.agent_registry[agent_type])
            return agent_class(config)
        
        return self.agent_registry[agent_type]
    
    async def execute_node(
        self, 
        node: DAGNode, 
        context: Dict[str, Any],
        workflow_execution_id: str = None
    ) -> bool:
        """
        执行单个节点
        
        Args:
            node: 要执行的节点
            context: 执行上下文
            workflow_execution_id: 工作流执行ID
            
        Returns:
            bool: 执行是否成功
        """
        logger.info(f"Starting execution of node {node.id}: {node.name}")
        
        # 检查是否应该跳过
        if node.should_skip(context):
            node.status = NodeStatus.SKIPPED
            logger.info(f"Node {node.id} skipped due to conditions")
            return True
        
        # 设置节点状态为运行中
        node.status = NodeStatus.RUNNING
        start_time = time.time()
        
        try:
            # 获取Agent
            agent = self.get_agent(node.agent_type, node.agent_config)
            if not agent:
                raise Exception(f"Agent not found: {node.agent_type}")
            
            # 准备输入数据
            input_data = self._prepare_input_data(node, context)
            
            # 执行任务（带超时）
            result = await asyncio.wait_for(
                agent.run(input_data, context),
                timeout=node.timeout_seconds
            )
            
            if result.success:
                node.status = NodeStatus.COMPLETED
                node.result = result.data
                
                # 更新上下文
                context[f"node_{node.id}_output"] = result.data
                context[f"node_{node.id}_metadata"] = result.metadata
                
                execution_time = int((time.time() - start_time) * 1000)
                logger.info(f"Node {node.id} completed successfully in {execution_time}ms")
                
                return True
            else:
                raise Exception(result.error_message or "Agent execution failed")
                
        except asyncio.TimeoutError:
            error_msg = f"Node {node.id} timed out after {node.timeout_seconds} seconds"
            logger.error(error_msg)
            node.status = NodeStatus.FAILED
            node.error_message = error_msg
            return False
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Node {node.id} failed: {error_msg}")
            
            # 检查是否需要重试
            if node.retry_count < node.max_retries:
                node.retry_count += 1
                node.status = NodeStatus.PENDING
                logger.info(f"Retrying node {node.id} (attempt {node.retry_count}/{node.max_retries})")
                return await self.execute_node(node, context, workflow_execution_id)
            else:
                node.status = NodeStatus.FAILED
                node.error_message = error_msg
                return False
    
    def _prepare_input_data(self, node: DAGNode, context: Dict[str, Any]) -> Dict[str, Any]:
        """准备节点的输入数据"""
        input_data = node.input_data.copy()
        
        # 处理依赖节点的输出作为输入
        for dep_id in node.dependencies:
            dep_output_key = f"node_{dep_id}_output"
            if dep_output_key in context:
                # 可以通过特殊的键名来引用依赖节点的输出
                input_data[f"dependency_{dep_id}"] = context[dep_output_key]
        
        # 处理模板变量替换
        input_data = self._resolve_template_variables(input_data, context)
        
        return input_data
    
    def _resolve_template_variables(self, data: Any, context: Dict[str, Any]) -> Any:
        """解析模板变量"""
        if isinstance(data, str):
            # 简单的模板变量替换，格式：${variable_name}
            import re
            pattern = r'\$\{([^}]+)\}'
            
            def replace_var(match):
                var_name = match.group(1)
                return str(context.get(var_name, match.group(0)))
            
            return re.sub(pattern, replace_var, data)
        
        elif isinstance(data, dict):
            return {k: self._resolve_template_variables(v, context) for k, v in data.items()}
        
        elif isinstance(data, list):
            return [self._resolve_template_variables(item, context) for item in data]
        
        else:
            return data
    
    def get_available_agents(self) -> Dict[str, Dict[str, Any]]:
        """获取所有可用的Agent信息"""
        return {
            agent_type: agent.get_info() 
            for agent_type, agent in self.agent_registry.items()
        }
