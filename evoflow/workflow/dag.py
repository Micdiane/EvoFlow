"""
工作流DAG（有向无环图）定义
"""
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field
from enum import Enum


class NodeStatus(Enum):
    """节点状态枚举"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class DAGNode:
    """DAG节点"""
    id: str
    name: str
    agent_type: str
    agent_config: Dict[str, Any] = field(default_factory=dict)
    input_data: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)  # 依赖的节点ID列表
    conditions: Dict[str, Any] = field(default_factory=dict)  # 执行条件
    retry_count: int = 0
    max_retries: int = 3
    timeout_seconds: int = 300
    status: NodeStatus = NodeStatus.PENDING
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    
    def can_execute(self, completed_nodes: Set[str]) -> bool:
        """检查节点是否可以执行"""
        if self.status != NodeStatus.PENDING:
            return False
        
        # 检查所有依赖是否已完成
        for dep in self.dependencies:
            if dep not in completed_nodes:
                return False
        
        return True
    
    def should_skip(self, context: Dict[str, Any]) -> bool:
        """检查节点是否应该跳过"""
        if not self.conditions:
            return False
        
        # 简单的条件检查逻辑
        condition_type = self.conditions.get("type")
        if condition_type == "skip_if":
            condition_value = self.conditions.get("value")
            context_key = self.conditions.get("context_key")
            if context_key in context:
                return context[context_key] == condition_value
        
        return False


class WorkflowDAG:
    """工作流DAG"""
    
    def __init__(self, nodes: List[DAGNode] = None):
        self.nodes: Dict[str, DAGNode] = {}
        self.edges: Dict[str, List[str]] = {}  # 节点ID -> 依赖节点ID列表
        
        if nodes:
            for node in nodes:
                self.add_node(node)
    
    def add_node(self, node: DAGNode) -> None:
        """添加节点"""
        self.nodes[node.id] = node
        self.edges[node.id] = node.dependencies.copy()
    
    def remove_node(self, node_id: str) -> None:
        """移除节点"""
        if node_id in self.nodes:
            del self.nodes[node_id]
        
        if node_id in self.edges:
            del self.edges[node_id]
        
        # 移除其他节点对此节点的依赖
        for edges in self.edges.values():
            if node_id in edges:
                edges.remove(node_id)
    
    def add_dependency(self, node_id: str, dependency_id: str) -> None:
        """添加依赖关系"""
        if node_id in self.nodes and dependency_id in self.nodes:
            if dependency_id not in self.edges[node_id]:
                self.edges[node_id].append(dependency_id)
                self.nodes[node_id].dependencies.append(dependency_id)
    
    def get_ready_nodes(self, completed_nodes: Set[str]) -> List[DAGNode]:
        """获取可以执行的节点"""
        ready_nodes = []
        
        for node in self.nodes.values():
            if node.can_execute(completed_nodes):
                ready_nodes.append(node)
        
        return ready_nodes
    
    def get_root_nodes(self) -> List[DAGNode]:
        """获取根节点（没有依赖的节点）"""
        root_nodes = []
        
        for node in self.nodes.values():
            if not node.dependencies:
                root_nodes.append(node)
        
        return root_nodes
    
    def validate(self) -> bool:
        """验证DAG是否有效（无环）"""
        # 使用拓扑排序检测环
        in_degree = {node_id: 0 for node_id in self.nodes}
        
        # 计算入度
        for node_id, dependencies in self.edges.items():
            for dep in dependencies:
                if dep in in_degree:
                    in_degree[node_id] += 1
        
        # 拓扑排序
        queue = [node_id for node_id, degree in in_degree.items() if degree == 0]
        processed = 0
        
        while queue:
            current = queue.pop(0)
            processed += 1
            
            # 减少依赖当前节点的节点的入度
            for node_id, dependencies in self.edges.items():
                if current in dependencies:
                    in_degree[node_id] -= 1
                    if in_degree[node_id] == 0:
                        queue.append(node_id)
        
        # 如果处理的节点数等于总节点数，则无环
        return processed == len(self.nodes)
    
    def get_execution_order(self) -> List[List[str]]:
        """获取执行顺序（按层级）"""
        if not self.validate():
            raise ValueError("DAG contains cycles")
        
        levels = []
        remaining_nodes = set(self.nodes.keys())
        completed_nodes = set()
        
        while remaining_nodes:
            current_level = []
            
            for node_id in list(remaining_nodes):
                node = self.nodes[node_id]
                if node.can_execute(completed_nodes):
                    current_level.append(node_id)
            
            if not current_level:
                raise ValueError("Unable to find executable nodes - possible circular dependency")
            
            levels.append(current_level)
            
            for node_id in current_level:
                remaining_nodes.remove(node_id)
                completed_nodes.add(node_id)
        
        return levels
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "nodes": [
                {
                    "id": node.id,
                    "name": node.name,
                    "agent_type": node.agent_type,
                    "agent_config": node.agent_config,
                    "input_data": node.input_data,
                    "dependencies": node.dependencies,
                    "conditions": node.conditions,
                    "max_retries": node.max_retries,
                    "timeout_seconds": node.timeout_seconds
                }
                for node in self.nodes.values()
            ]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WorkflowDAG':
        """从字典创建DAG"""
        nodes = []
        
        for node_data in data.get("nodes", []):
            node = DAGNode(
                id=node_data["id"],
                name=node_data["name"],
                agent_type=node_data["agent_type"],
                agent_config=node_data.get("agent_config", {}),
                input_data=node_data.get("input_data", {}),
                dependencies=node_data.get("dependencies", []),
                conditions=node_data.get("conditions", {}),
                max_retries=node_data.get("max_retries", 3),
                timeout_seconds=node_data.get("timeout_seconds", 300)
            )
            nodes.append(node)
        
        return cls(nodes)
