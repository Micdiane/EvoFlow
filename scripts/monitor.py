#!/usr/bin/env python3
"""
EvoFlow 性能监控脚本
"""
import asyncio
import time
import psutil
import httpx
from datetime import datetime
from typing import Dict, Any


class EvoFlowMonitor:
    """EvoFlow性能监控器"""
    
    def __init__(self, api_url: str = "http://localhost:8000"):
        self.api_url = api_url
        self.monitoring = False
        
    async def check_api_health(self) -> Dict[str, Any]:
        """检查API健康状态"""
        try:
            start_time = time.time()
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.api_url}/health")
                response_time = (time.time() - start_time) * 1000
                
                if response.status_code == 200:
                    return {
                        "status": "healthy",
                        "response_time_ms": round(response_time, 2),
                        "status_code": response.status_code
                    }
                else:
                    return {
                        "status": "unhealthy",
                        "response_time_ms": round(response_time, 2),
                        "status_code": response.status_code
                    }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "response_time_ms": None
            }
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """获取系统指标"""
        try:
            # CPU使用率
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # 内存使用情况
            memory = psutil.virtual_memory()
            
            # 磁盘使用情况
            disk = psutil.disk_usage('/')
            
            # 网络统计
            network = psutil.net_io_counters()
            
            return {
                "cpu": {
                    "percent": cpu_percent,
                    "count": psutil.cpu_count()
                },
                "memory": {
                    "total_gb": round(memory.total / (1024**3), 2),
                    "used_gb": round(memory.used / (1024**3), 2),
                    "percent": memory.percent,
                    "available_gb": round(memory.available / (1024**3), 2)
                },
                "disk": {
                    "total_gb": round(disk.total / (1024**3), 2),
                    "used_gb": round(disk.used / (1024**3), 2),
                    "free_gb": round(disk.free / (1024**3), 2),
                    "percent": round((disk.used / disk.total) * 100, 2)
                },
                "network": {
                    "bytes_sent": network.bytes_sent,
                    "bytes_recv": network.bytes_recv,
                    "packets_sent": network.packets_sent,
                    "packets_recv": network.packets_recv
                }
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def get_docker_stats(self) -> Dict[str, Any]:
        """获取Docker容器统计信息"""
        try:
            import subprocess
            import json
            
            # 获取容器列表
            result = subprocess.run(
                ["docker", "ps", "--format", "{{.Names}}"],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                return {"error": "Docker not available"}
            
            container_names = result.stdout.strip().split('\n')
            container_stats = {}
            
            for name in container_names:
                if not name:
                    continue
                    
                # 获取容器统计信息
                stats_result = subprocess.run(
                    ["docker", "stats", name, "--no-stream", "--format", 
                     "{{.CPUPerc}},{{.MemUsage}},{{.NetIO}},{{.BlockIO}}"],
                    capture_output=True,
                    text=True
                )
                
                if stats_result.returncode == 0:
                    stats_line = stats_result.stdout.strip()
                    if stats_line:
                        parts = stats_line.split(',')
                        if len(parts) >= 4:
                            container_stats[name] = {
                                "cpu_percent": parts[0],
                                "memory_usage": parts[1],
                                "network_io": parts[2],
                                "block_io": parts[3]
                            }
            
            return container_stats
            
        except Exception as e:
            return {"error": str(e)}
    
    async def get_api_metrics(self) -> Dict[str, Any]:
        """获取API指标"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # 获取工作流数量
                workflows_response = await client.get(f"{self.api_url}/api/v1/workflows/")
                workflows_count = len(workflows_response.json()) if workflows_response.status_code == 200 else 0
                
                # 获取执行数量
                executions_response = await client.get(f"{self.api_url}/api/v1/executions/")
                executions_count = len(executions_response.json()) if executions_response.status_code == 200 else 0
                
                # 获取Agent数量
                agents_response = await client.get(f"{self.api_url}/api/v1/agents/")
                agents_count = len(agents_response.json()) if agents_response.status_code == 200 else 0
                
                return {
                    "workflows_count": workflows_count,
                    "executions_count": executions_count,
                    "agents_count": agents_count
                }
        except Exception as e:
            return {"error": str(e)}
    
    def format_metrics_display(self, metrics: Dict[str, Any]) -> str:
        """格式化指标显示"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        display = f"\n{'='*60}\n"
        display += f"📊 EvoFlow 监控报告 - {timestamp}\n"
        display += f"{'='*60}\n"
        
        # API健康状态
        api_health = metrics.get("api_health", {})
        status_emoji = "✅" if api_health.get("status") == "healthy" else "❌"
        display += f"\n🌐 API状态: {status_emoji} {api_health.get('status', 'unknown')}\n"
        if api_health.get("response_time_ms"):
            display += f"   响应时间: {api_health['response_time_ms']}ms\n"
        
        # 系统指标
        system = metrics.get("system", {})
        if "error" not in system:
            display += f"\n💻 系统资源:\n"
            display += f"   CPU: {system['cpu']['percent']}% ({system['cpu']['count']} cores)\n"
            display += f"   内存: {system['memory']['used_gb']:.1f}GB / {system['memory']['total_gb']:.1f}GB ({system['memory']['percent']}%)\n"
            display += f"   磁盘: {system['disk']['used_gb']:.1f}GB / {system['disk']['total_gb']:.1f}GB ({system['disk']['percent']}%)\n"
        
        # Docker容器状态
        docker_stats = metrics.get("docker_stats", {})
        if "error" not in docker_stats and docker_stats:
            display += f"\n🐳 Docker容器:\n"
            for name, stats in docker_stats.items():
                display += f"   {name}: CPU {stats['cpu_percent']}, 内存 {stats['memory_usage']}\n"
        
        # API指标
        api_metrics = metrics.get("api_metrics", {})
        if "error" not in api_metrics:
            display += f"\n📈 API指标:\n"
            display += f"   工作流数量: {api_metrics.get('workflows_count', 0)}\n"
            display += f"   执行记录: {api_metrics.get('executions_count', 0)}\n"
            display += f"   Agent数量: {api_metrics.get('agents_count', 0)}\n"
        
        return display
    
    async def collect_metrics(self) -> Dict[str, Any]:
        """收集所有指标"""
        metrics = {}
        
        # 并行收集指标
        tasks = [
            ("api_health", self.check_api_health()),
            ("api_metrics", self.get_api_metrics()),
            ("docker_stats", self.get_docker_stats())
        ]
        
        results = await asyncio.gather(*[task[1] for task in tasks], return_exceptions=True)
        
        for i, (name, _) in enumerate(tasks):
            result = results[i]
            if isinstance(result, Exception):
                metrics[name] = {"error": str(result)}
            else:
                metrics[name] = result
        
        # 同步收集系统指标
        metrics["system"] = self.get_system_metrics()
        
        return metrics
    
    async def monitor_once(self):
        """执行一次监控"""
        print("📊 收集监控数据...")
        metrics = await self.collect_metrics()
        display = self.format_metrics_display(metrics)
        print(display)
        return metrics
    
    async def monitor_continuous(self, interval: int = 30):
        """持续监控"""
        print(f"🔄 开始持续监控 (间隔: {interval}秒)")
        print("按 Ctrl+C 停止监控")
        
        self.monitoring = True
        
        try:
            while self.monitoring:
                await self.monitor_once()
                await asyncio.sleep(interval)
        except KeyboardInterrupt:
            print("\n⏹️  监控已停止")
            self.monitoring = False
    
    def stop_monitoring(self):
        """停止监控"""
        self.monitoring = False


async def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="EvoFlow 性能监控")
    parser.add_argument("--url", default="http://localhost:8000", help="API URL")
    parser.add_argument("--interval", type=int, default=30, help="监控间隔（秒）")
    parser.add_argument("--once", action="store_true", help="只执行一次监控")
    
    args = parser.parse_args()
    
    monitor = EvoFlowMonitor(args.url)
    
    if args.once:
        await monitor.monitor_once()
    else:
        await monitor.monitor_continuous(args.interval)


if __name__ == "__main__":
    asyncio.run(main())
