"""
基础功能测试
"""
import pytest
from evoflow.config import settings
from evoflow.workflow.dag import DAGNode, WorkflowDAG
from evoflow.utils.validators import validate_dag, validate_agent_config


def test_settings():
    """测试配置加载"""
    assert settings.app_name == "EvoFlow"
    assert settings.app_version == "0.1.0"
    assert settings.deepseek_api_key is not None


def test_dag_creation():
    """测试DAG创建"""
    nodes = [
        DAGNode(
            id="node1",
            name="测试节点1",
            agent_type="web_search",
            input_data={"query": "test"}
        ),
        DAGNode(
            id="node2", 
            name="测试节点2",
            agent_type="text_writing",
            input_data={"prompt": "test"},
            dependencies=["node1"]
        )
    ]
    
    dag = WorkflowDAG(nodes)
    assert len(dag.nodes) == 2
    assert dag.validate() == True
    
    execution_order = dag.get_execution_order()
    assert len(execution_order) == 2
    assert execution_order[0] == ["node1"]
    assert execution_order[1] == ["node2"]


def test_dag_validation():
    """测试DAG验证"""
    # 有效的DAG
    valid_dag = {
        "nodes": [
            {
                "id": "node1",
                "name": "节点1",
                "agent_type": "web_search",
                "input_data": {"query": "test"}
            }
        ]
    }
    
    is_valid, error = validate_dag(valid_dag)
    assert is_valid == True
    assert error == ""
    
    # 无效的DAG（缺少必需字段）
    invalid_dag = {
        "nodes": [
            {
                "id": "node1",
                "name": "节点1"
                # 缺少agent_type
            }
        ]
    }
    
    is_valid, error = validate_dag(invalid_dag)
    assert is_valid == False
    assert "missing required field" in error


def test_agent_config_validation():
    """测试Agent配置验证"""
    # 有效的配置
    valid_config = {
        "max_results": 10,
        "timeout": 30
    }
    
    is_valid, error = validate_agent_config("web_search", valid_config)
    assert is_valid == True
    assert error == ""
    
    # 无效的配置
    invalid_config = {
        "max_results": -1,  # 负数无效
        "timeout": 30
    }
    
    is_valid, error = validate_agent_config("web_search", invalid_config)
    assert is_valid == False
    assert "positive integer" in error


def test_circular_dependency_detection():
    """测试循环依赖检测"""
    # 创建有循环依赖的DAG
    circular_dag = {
        "nodes": [
            {
                "id": "node1",
                "name": "节点1", 
                "agent_type": "web_search",
                "dependencies": ["node2"]
            },
            {
                "id": "node2",
                "name": "节点2",
                "agent_type": "text_writing", 
                "dependencies": ["node1"]
            }
        ]
    }
    
    is_valid, error = validate_dag(circular_dag)
    assert is_valid == False
    assert "circular dependencies" in error


if __name__ == "__main__":
    pytest.main([__file__])
