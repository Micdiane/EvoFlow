#!/usr/bin/env python3
"""
API测试脚本
"""
import asyncio
import httpx
import json
from typing import Dict, Any


class EvoFlowAPITester:
    """EvoFlow API测试器"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api/v1"
        
    async def test_health_check(self):
        """测试健康检查"""
        print("🏥 测试健康检查...")
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{self.base_url}/health")
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ 健康检查通过: {data['status']}")
                    return True
                else:
                    print(f"❌ 健康检查失败: {response.status_code}")
                    return False
            except Exception as e:
                print(f"❌ 健康检查异常: {e}")
                return False
    
    async def test_list_agents(self):
        """测试获取Agent列表"""
        print("\n🤖 测试获取Agent列表...")
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{self.api_url}/agents/")
                if response.status_code == 200:
                    agents = response.json()
                    print(f"✅ 获取到 {len(agents)} 个Agent:")
                    for agent in agents:
                        print(f"   • {agent['name']} ({agent['type']})")
                    return agents
                else:
                    print(f"❌ 获取Agent列表失败: {response.status_code}")
                    return []
            except Exception as e:
                print(f"❌ 获取Agent列表异常: {e}")
                return []
    
    async def test_get_available_agents(self):
        """测试获取可用Agent"""
        print("\n🔍 测试获取可用Agent...")
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{self.api_url}/agents/available")
                if response.status_code == 200:
                    data = response.json()
                    agents = data.get("agents", {})
                    print(f"✅ 可用Agent类型: {list(agents.keys())}")
                    return agents
                else:
                    print(f"❌ 获取可用Agent失败: {response.status_code}")
                    return {}
            except Exception as e:
                print(f"❌ 获取可用Agent异常: {e}")
                return {}
    
    async def test_agent_functionality(self, agent_id: str):
        """测试Agent功能"""
        print(f"\n🧪 测试Agent功能 (ID: {agent_id})...")
        
        # 不同类型Agent的测试数据
        test_data_map = {
            "web_search": {
                "query": "Python编程教程",
                "max_results": 3
            },
            "text_writing": {
                "prompt": "写一首关于春天的短诗",
                "task_type": "creative",
                "max_tokens": 200,
                "temperature": 0.8
            },
            "data_analysis": {
                "data_source": [
                    {"name": "Alice", "age": 25, "score": 85},
                    {"name": "Bob", "age": 30, "score": 92},
                    {"name": "Charlie", "age": 28, "score": 78}
                ],
                "analysis_type": "basic_stats",
                "columns": ["age", "score"]
            },
            "file_processor": {
                "operation": "read",
                "file_data": "name,age,city\nAlice,25,New York\nBob,30,London",
                "file_format": "csv"
            }
        }
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                # 首先获取Agent信息
                agent_response = await client.get(f"{self.api_url}/agents/{agent_id}")
                if agent_response.status_code != 200:
                    print(f"❌ 获取Agent信息失败: {agent_response.status_code}")
                    return False
                
                agent_info = agent_response.json()
                agent_type = agent_info.get("type")
                
                # 选择测试数据
                test_data = test_data_map.get(agent_type, {"test": "data"})
                
                # 测试Agent
                response = await client.post(
                    f"{self.api_url}/agents/{agent_id}/test",
                    json=test_data
                )
                
                if response.status_code == 200:
                    result = response.json()
                    test_result = result.get("test_result", {})
                    
                    print(f"✅ Agent测试成功:")
                    print(f"   • Agent: {result.get('agent_name')}")
                    print(f"   • 成功: {test_result.get('success')}")
                    print(f"   • 执行时间: {test_result.get('execution_time_ms')}ms")
                    print(f"   • 成本估算: ${test_result.get('cost_estimate', 0):.4f}")
                    
                    if test_result.get("error_message"):
                        print(f"   • 错误: {test_result['error_message']}")
                    
                    return True
                else:
                    print(f"❌ Agent测试失败: {response.status_code}")
                    try:
                        error_detail = response.json()
                        print(f"   错误详情: {error_detail}")
                    except:
                        print(f"   响应内容: {response.text}")
                    return False
                    
            except Exception as e:
                print(f"❌ Agent测试异常: {e}")
                return False
    
    async def test_create_workflow(self):
        """测试创建工作流"""
        print("\n📋 测试创建工作流...")
        
        workflow_data = {
            "name": "API测试工作流",
            "description": "通过API创建的测试工作流",
            "dag_definition": {
                "nodes": [
                    {
                        "id": "test_search",
                        "name": "测试搜索",
                        "agent_type": "web_search",
                        "agent_config": {},
                        "input_data": {
                            "query": "EvoFlow工作流平台",
                            "max_results": 3
                        },
                        "dependencies": [],
                        "conditions": {},
                        "max_retries": 2,
                        "timeout_seconds": 60
                    }
                ]
            }
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.api_url}/workflows/",
                    json=workflow_data
                )
                
                if response.status_code == 200:
                    workflow = response.json()
                    print(f"✅ 工作流创建成功:")
                    print(f"   • ID: {workflow['id']}")
                    print(f"   • 名称: {workflow['name']}")
                    print(f"   • 状态: {workflow['status']}")
                    return workflow
                else:
                    print(f"❌ 工作流创建失败: {response.status_code}")
                    try:
                        error_detail = response.json()
                        print(f"   错误详情: {error_detail}")
                    except:
                        print(f"   响应内容: {response.text}")
                    return None
                    
            except Exception as e:
                print(f"❌ 工作流创建异常: {e}")
                return None
    
    async def test_execute_workflow(self, workflow_id: str):
        """测试执行工作流"""
        print(f"\n▶️  测试执行工作流 (ID: {workflow_id})...")
        
        execute_data = {
            "input_data": {
                "user_request": "测试工作流执行"
            }
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.api_url}/workflows/{workflow_id}/execute",
                    json=execute_data
                )
                
                if response.status_code == 200:
                    result = response.json()
                    execution_id = result.get("execution_id")
                    print(f"✅ 工作流执行启动成功:")
                    print(f"   • 执行ID: {execution_id}")
                    print(f"   • 状态: {result.get('status')}")
                    return execution_id
                else:
                    print(f"❌ 工作流执行失败: {response.status_code}")
                    try:
                        error_detail = response.json()
                        print(f"   错误详情: {error_detail}")
                    except:
                        print(f"   响应内容: {response.text}")
                    return None
                    
            except Exception as e:
                print(f"❌ 工作流执行异常: {e}")
                return None
    
    async def test_execution_status(self, execution_id: str):
        """测试获取执行状态"""
        print(f"\n📊 测试获取执行状态 (ID: {execution_id})...")
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{self.api_url}/executions/{execution_id}")
                
                if response.status_code == 200:
                    status = response.json()
                    print(f"✅ 执行状态获取成功:")
                    print(f"   • 状态: {status.get('status')}")
                    print(f"   • 开始时间: {status.get('started_at')}")
                    print(f"   • 完成时间: {status.get('completed_at')}")
                    
                    if status.get("error_message"):
                        print(f"   • 错误: {status['error_message']}")
                    
                    return status
                else:
                    print(f"❌ 获取执行状态失败: {response.status_code}")
                    return None
                    
            except Exception as e:
                print(f"❌ 获取执行状态异常: {e}")
                return None
    
    async def run_all_tests(self):
        """运行所有测试"""
        print("🧪 开始EvoFlow API测试")
        print("=" * 50)
        
        # 1. 健康检查
        health_ok = await self.test_health_check()
        if not health_ok:
            print("❌ 健康检查失败，停止测试")
            return
        
        # 2. 获取Agent列表
        agents = await self.test_list_agents()
        
        # 3. 获取可用Agent
        available_agents = await self.test_get_available_agents()
        
        # 4. 测试Agent功能（如果有Agent）
        if agents:
            agent_id = agents[0]["id"]
            await self.test_agent_functionality(agent_id)
        
        # 5. 创建工作流
        workflow = await self.test_create_workflow()
        
        # 6. 执行工作流（如果创建成功）
        if workflow:
            # 首先激活工作流
            workflow_id = workflow["id"]
            
            # 执行工作流
            execution_id = await self.test_execute_workflow(workflow_id)
            
            # 7. 检查执行状态（如果执行成功）
            if execution_id:
                await asyncio.sleep(2)  # 等待一下
                await self.test_execution_status(execution_id)
        
        print("\n" + "=" * 50)
        print("🎉 API测试完成！")


async def main():
    """主函数"""
    tester = EvoFlowAPITester()
    await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())
