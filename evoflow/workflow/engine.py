"""
工作流执行引擎
"""
import asyncio
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime

from loguru import logger

from .dag import WorkflowDAG, DAGNode, NodeStatus
from .executor import TaskExecutor
from ..models import WorkflowExecution, TaskExecution
from ..database import AsyncSessionLocal


class WorkflowEngine:
    """工作流执行引擎"""
    
    def __init__(self):
        self.executor = TaskExecutor()
        self.running_workflows: Dict[str, asyncio.Task] = {}
    
    async def execute_workflow(
        self, 
        workflow_id: str,
        dag_definition: Dict[str, Any],
        input_data: Dict[str, Any] = None,
        user_id: str = None
    ) -> str:
        """
        执行工作流
        
        Args:
            workflow_id: 工作流ID
            dag_definition: DAG定义
            input_data: 输入数据
            user_id: 用户ID
            
        Returns:
            str: 执行ID
        """
        execution_id = str(uuid.uuid4())
        
        # 创建执行记录
        async with AsyncSessionLocal() as db:
            execution = WorkflowExecution(
                id=execution_id,
                workflow_id=workflow_id,
                status="running",
                input_data=input_data or {},
                started_at=datetime.utcnow()
            )
            db.add(execution)
            await db.commit()
        
        # 启动异步执行任务
        task = asyncio.create_task(
            self._run_workflow(execution_id, workflow_id, dag_definition, input_data or {})
        )
        self.running_workflows[execution_id] = task
        
        logger.info(f"Started workflow execution {execution_id} for workflow {workflow_id}")
        return execution_id
    
    async def _run_workflow(
        self,
        execution_id: str,
        workflow_id: str, 
        dag_definition: Dict[str, Any],
        input_data: Dict[str, Any]
    ) -> None:
        """运行工作流的内部方法"""
        try:
            # 创建DAG
            dag = WorkflowDAG.from_dict(dag_definition)
            
            # 验证DAG
            if not dag.validate():
                raise ValueError("Invalid DAG: contains cycles")
            
            # 初始化执行上下文
            context = {
                "workflow_id": workflow_id,
                "execution_id": execution_id,
                "input_data": input_data,
                "start_time": datetime.utcnow()
            }
            context.update(input_data)
            
            # 执行工作流
            success = await self._execute_dag(dag, context, execution_id)
            
            # 更新执行状态
            await self._update_execution_status(
                execution_id, 
                "completed" if success else "failed",
                context
            )
            
            logger.info(f"Workflow execution {execution_id} {'completed' if success else 'failed'}")
            
        except Exception as e:
            logger.error(f"Workflow execution {execution_id} failed with error: {str(e)}")
            await self._update_execution_status(execution_id, "failed", {}, str(e))
        
        finally:
            # 清理运行中的任务
            if execution_id in self.running_workflows:
                del self.running_workflows[execution_id]
    
    async def _execute_dag(
        self, 
        dag: WorkflowDAG, 
        context: Dict[str, Any],
        execution_id: str
    ) -> bool:
        """执行DAG"""
        completed_nodes = set()
        failed_nodes = set()
        
        # 获取执行顺序
        execution_levels = dag.get_execution_order()
        
        for level in execution_levels:
            # 并行执行同一层级的节点
            tasks = []
            level_nodes = []
            
            for node_id in level:
                node = dag.nodes[node_id]
                if node.status == NodeStatus.PENDING:
                    level_nodes.append(node)
                    task = asyncio.create_task(
                        self._execute_node_with_tracking(node, context, execution_id)
                    )
                    tasks.append(task)
            
            if tasks:
                # 等待所有任务完成
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # 处理结果
                for i, result in enumerate(results):
                    node = level_nodes[i]
                    
                    if isinstance(result, Exception):
                        logger.error(f"Node {node.id} failed with exception: {result}")
                        failed_nodes.add(node.id)
                        node.status = NodeStatus.FAILED
                        node.error_message = str(result)
                    elif result:
                        completed_nodes.add(node.id)
                    else:
                        failed_nodes.add(node.id)
        
        # 检查是否有失败的关键节点
        critical_failed = any(
            node_id in failed_nodes and not dag.nodes[node_id].conditions.get("optional", False)
            for node_id in failed_nodes
        )
        
        return len(failed_nodes) == 0 or not critical_failed
    
    async def _execute_node_with_tracking(
        self,
        node: DAGNode,
        context: Dict[str, Any],
        execution_id: str
    ) -> bool:
        """执行节点并记录到数据库"""
        # 创建任务执行记录
        task_execution_id = str(uuid.uuid4())
        
        async with AsyncSessionLocal() as db:
            # 查找对应的Agent
            from ..models import Agent
            agent = await db.query(Agent).filter(Agent.type == node.agent_type).first()
            
            task_execution = TaskExecution(
                id=task_execution_id,
                workflow_execution_id=execution_id,
                agent_id=agent.id if agent else None,
                task_name=node.name,
                status="running",
                input_data=node.input_data,
                started_at=datetime.utcnow()
            )
            db.add(task_execution)
            await db.commit()
        
        # 执行节点
        success = await self.executor.execute_node(node, context, execution_id)
        
        # 更新任务执行记录
        async with AsyncSessionLocal() as db:
            task_execution = await db.get(TaskExecution, task_execution_id)
            if task_execution:
                task_execution.status = "completed" if success else "failed"
                task_execution.output_data = node.result
                task_execution.error_message = node.error_message
                task_execution.completed_at = datetime.utcnow()
                
                if hasattr(node, 'execution_time_ms'):
                    task_execution.execution_time_ms = node.execution_time_ms
                
                await db.commit()
        
        return success
    
    async def _update_execution_status(
        self,
        execution_id: str,
        status: str,
        context: Dict[str, Any],
        error_message: str = None
    ) -> None:
        """更新执行状态"""
        async with AsyncSessionLocal() as db:
            execution = await db.get(WorkflowExecution, execution_id)
            if execution:
                execution.status = status
                execution.completed_at = datetime.utcnow()
                
                if error_message:
                    execution.error_message = error_message
                
                # 提取输出数据
                output_data = {}
                for key, value in context.items():
                    if key.startswith("node_") and key.endswith("_output"):
                        output_data[key] = value
                
                execution.output_data = output_data
                await db.commit()
    
    async def cancel_workflow(self, execution_id: str) -> bool:
        """取消工作流执行"""
        if execution_id in self.running_workflows:
            task = self.running_workflows[execution_id]
            task.cancel()
            
            # 更新状态
            await self._update_execution_status(execution_id, "cancelled", {})
            
            logger.info(f"Cancelled workflow execution {execution_id}")
            return True
        
        return False
    
    async def get_execution_status(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """获取执行状态"""
        async with AsyncSessionLocal() as db:
            execution = await db.get(WorkflowExecution, execution_id)
            if execution:
                return {
                    "id": str(execution.id),
                    "workflow_id": str(execution.workflow_id),
                    "status": execution.status,
                    "started_at": execution.started_at.isoformat() if execution.started_at else None,
                    "completed_at": execution.completed_at.isoformat() if execution.completed_at else None,
                    "input_data": execution.input_data,
                    "output_data": execution.output_data,
                    "error_message": execution.error_message
                }
        
        return None
    
    def get_available_agents(self) -> Dict[str, Dict[str, Any]]:
        """获取可用的Agent列表"""
        return self.executor.get_available_agents()
