"""
测试各个Agent的功能
"""
import asyncio
from evoflow.agents import (
    WebSearchAgent, TextWritingAgent, DataAnalysisAgent,
    EmailSenderAgent, FileProcessorAgent
)


async def test_web_search_agent():
    """测试网络搜索Agent"""
    print("=== 测试WebSearchAgent ===")
    
    agent = WebSearchAgent()
    
    input_data = {
        "query": "Python异步编程",
        "max_results": 3
    }
    
    result = await agent.run(input_data, {})
    
    print(f"执行结果: {result.success}")
    print(f"搜索结果数量: {len(result.data.get('results', []))}")
    print(f"执行时间: {result.execution_time_ms}ms")
    print(f"成本估算: ${result.cost_estimate}")
    
    if result.success:
        for i, item in enumerate(result.data["results"]):
            print(f"  {i+1}. {item['title']}")
    else:
        print(f"错误: {result.error_message}")


async def test_text_writing_agent():
    """测试文本生成Agent"""
    print("\n=== 测试TextWritingAgent ===")
    
    agent = TextWritingAgent()
    
    input_data = {
        "prompt": "请写一篇关于人工智能在医疗领域应用的短文",
        "task_type": "general",
        "max_tokens": 500,
        "temperature": 0.7
    }
    
    result = await agent.run(input_data, {})
    
    print(f"执行结果: {result.success}")
    print(f"执行时间: {result.execution_time_ms}ms")
    print(f"成本估算: ${result.cost_estimate}")
    
    if result.success:
        print(f"生成的文本:\n{result.data['generated_text']}")
    else:
        print(f"错误: {result.error_message}")


async def test_data_analysis_agent():
    """测试数据分析Agent"""
    print("\n=== 测试DataAnalysisAgent ===")
    
    agent = DataAnalysisAgent()
    
    # 创建测试数据
    test_data = [
        {"name": "Alice", "age": 25, "salary": 50000},
        {"name": "Bob", "age": 30, "salary": 60000},
        {"name": "Charlie", "age": 35, "salary": 70000},
        {"name": "Diana", "age": 28, "salary": 55000}
    ]
    
    input_data = {
        "data_source": test_data,
        "analysis_type": "basic_stats",
        "columns": ["age", "salary"]
    }
    
    result = await agent.run(input_data, {})
    
    print(f"执行结果: {result.success}")
    print(f"执行时间: {result.execution_time_ms}ms")
    print(f"成本估算: ${result.cost_estimate}")
    
    if result.success:
        print(f"数据形状: {result.data['data_shape']}")
        print(f"分析结果: {result.data['analysis_result']}")
    else:
        print(f"错误: {result.error_message}")


async def test_file_processor_agent():
    """测试文件处理Agent"""
    print("\n=== 测试FileProcessorAgent ===")
    
    agent = FileProcessorAgent()
    
    # 测试读取CSV文件
    csv_data = """name,age,city
Alice,25,New York
Bob,30,London
Charlie,35,Tokyo"""
    
    input_data = {
        "operation": "read",
        "file_data": csv_data,
        "file_format": "csv"
    }
    
    result = await agent.run(input_data, {})
    
    print(f"执行结果: {result.success}")
    print(f"执行时间: {result.execution_time_ms}ms")
    print(f"成本估算: ${result.cost_estimate}")
    
    if result.success:
        print(f"文件类型: {result.data['result']['type']}")
        print(f"行数: {result.data['result']['row_count']}")
        print(f"列名: {result.data['result']['columns']}")
    else:
        print(f"错误: {result.error_message}")


async def main():
    """运行所有测试"""
    await test_web_search_agent()
    await test_text_writing_agent()
    await test_data_analysis_agent()
    await test_file_processor_agent()


if __name__ == "__main__":
    asyncio.run(main())
