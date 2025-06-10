"""
验证工具
"""
from typing import Dict, Any, List


def validate_dag(dag_definition: Dict[str, Any]) -> tuple[bool, str]:
    """
    验证DAG定义是否有效
    
    Args:
        dag_definition: DAG定义字典
        
    Returns:
        tuple: (是否有效, 错误信息)
    """
    try:
        if not isinstance(dag_definition, dict):
            return False, "DAG definition must be a dictionary"
        
        nodes = dag_definition.get("nodes", [])
        if not isinstance(nodes, list):
            return False, "Nodes must be a list"
        
        if len(nodes) == 0:
            return False, "DAG must contain at least one node"
        
        node_ids = set()
        
        # 验证每个节点
        for i, node in enumerate(nodes):
            if not isinstance(node, dict):
                return False, f"Node {i} must be a dictionary"
            
            # 检查必需字段
            required_fields = ["id", "name", "agent_type"]
            for field in required_fields:
                if field not in node:
                    return False, f"Node {i} missing required field: {field}"
            
            node_id = node["id"]
            if node_id in node_ids:
                return False, f"Duplicate node ID: {node_id}"
            
            node_ids.add(node_id)
            
            # 验证依赖关系
            dependencies = node.get("dependencies", [])
            if not isinstance(dependencies, list):
                return False, f"Node {node_id} dependencies must be a list"
        
        # 验证依赖关系的有效性
        for node in nodes:
            node_id = node["id"]
            dependencies = node.get("dependencies", [])
            
            for dep in dependencies:
                if dep not in node_ids:
                    return False, f"Node {node_id} depends on non-existent node: {dep}"
                
                if dep == node_id:
                    return False, f"Node {node_id} cannot depend on itself"
        
        # 检查循环依赖
        if _has_circular_dependency(nodes):
            return False, "DAG contains circular dependencies"
        
        return True, ""
        
    except Exception as e:
        return False, f"DAG validation error: {str(e)}"


def _has_circular_dependency(nodes: List[Dict[str, Any]]) -> bool:
    """检查是否存在循环依赖"""
    # 构建邻接表
    graph = {}
    in_degree = {}
    
    for node in nodes:
        node_id = node["id"]
        dependencies = node.get("dependencies", [])
        
        graph[node_id] = dependencies
        in_degree[node_id] = len(dependencies)
    
    # 拓扑排序检测环
    queue = [node_id for node_id, degree in in_degree.items() if degree == 0]
    processed = 0
    
    while queue:
        current = queue.pop(0)
        processed += 1
        
        # 减少依赖当前节点的节点的入度
        for node_id, dependencies in graph.items():
            if current in dependencies:
                in_degree[node_id] -= 1
                if in_degree[node_id] == 0:
                    queue.append(node_id)
    
    # 如果处理的节点数不等于总节点数，则存在环
    return processed != len(nodes)


def validate_agent_config(agent_type: str, config: Dict[str, Any]) -> tuple[bool, str]:
    """
    验证Agent配置是否有效
    
    Args:
        agent_type: Agent类型
        config: Agent配置
        
    Returns:
        tuple: (是否有效, 错误信息)
    """
    try:
        if not isinstance(config, dict):
            return False, "Agent config must be a dictionary"
        
        # 根据Agent类型验证特定配置
        if agent_type == "web_search":
            max_results = config.get("max_results", 10)
            if not isinstance(max_results, int) or max_results <= 0:
                return False, "max_results must be a positive integer"
            
            timeout = config.get("timeout", 30)
            if not isinstance(timeout, (int, float)) or timeout <= 0:
                return False, "timeout must be a positive number"
        
        elif agent_type == "text_writing":
            max_tokens = config.get("max_tokens", 2000)
            if not isinstance(max_tokens, int) or max_tokens <= 0:
                return False, "max_tokens must be a positive integer"
            
            temperature = config.get("temperature", 0.7)
            if not isinstance(temperature, (int, float)) or temperature < 0 or temperature > 2:
                return False, "temperature must be between 0 and 2"
        
        elif agent_type == "email_sender":
            smtp_server = config.get("smtp_server")
            if smtp_server and not isinstance(smtp_server, str):
                return False, "smtp_server must be a string"
            
            smtp_port = config.get("smtp_port", 587)
            if not isinstance(smtp_port, int) or smtp_port <= 0:
                return False, "smtp_port must be a positive integer"
        
        return True, ""
        
    except Exception as e:
        return False, f"Agent config validation error: {str(e)}"
