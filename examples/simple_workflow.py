"""
简单工作流示例
"""
import asyncio
import json
from evoflow.workflow.dag import DAGNode, WorkflowDAG
from evoflow.workflow.engine import WorkflowEngine


async def create_simple_workflow():
    """创建一个简单的工作流示例"""
    
    # 创建节点
    nodes = [
        DAGNode(
            id="search_node",
            name="搜索信息",
            agent_type="web_search",
            input_data={
                "query": "人工智能最新发展",
                "max_results": 5
            },
            dependencies=[]
        ),
        DAGNode(
            id="analyze_node", 
            name="分析搜索结果",
            agent_type="text_writing",
            input_data={
                "prompt": "请分析以下搜索结果，总结人工智能的最新发展趋势：${dependency_search_node}",
                "task_type": "summary",
                "max_tokens": 1000
            },
            dependencies=["search_node"]
        ),
        DAGNode(
            id="report_node",
            name="生成报告",
            agent_type="text_writing", 
            input_data={
                "prompt": "基于以下分析，生成一份专业的AI发展趋势报告：${dependency_analyze_node}",
                "task_type": "business",
                "max_tokens": 2000
            },
            dependencies=["analyze_node"]
        )
    ]
    
    # 创建DAG
    dag = WorkflowDAG(nodes)
    
    # 验证DAG
    if not dag.validate():
        print("DAG验证失败")
        return
    
    print("DAG验证成功")
    print(f"执行顺序: {dag.get_execution_order()}")
    
    # 创建工作流引擎
    engine = WorkflowEngine()
    
    # 执行工作流
    execution_id = await engine.execute_workflow(
        workflow_id="simple_workflow_001",
        dag_definition=dag.to_dict(),
        input_data={"user_query": "人工智能最新发展"}
    )
    
    print(f"工作流执行ID: {execution_id}")
    
    # 等待执行完成并获取状态
    import time
    for i in range(30):  # 最多等待30秒
        status = await engine.get_execution_status(execution_id)
        if status:
            print(f"执行状态: {status['status']}")
            if status["status"] in ["completed", "failed", "cancelled"]:
                print(f"执行结果: {json.dumps(status, indent=2, ensure_ascii=False)}")
                break
        
        await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(create_simple_workflow())
