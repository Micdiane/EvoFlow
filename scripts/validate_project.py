#!/usr/bin/env python3
"""
EvoFlow 项目完整性验证脚本
"""
import os
import sys
import json
import asyncio
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple


class ProjectValidator:
    """项目验证器"""
    
    def __init__(self):
        self.project_root = Path.cwd()
        self.errors = []
        self.warnings = []
        self.passed_checks = []
    
    def log_error(self, message: str):
        """记录错误"""
        self.errors.append(message)
        print(f"❌ {message}")
    
    def log_warning(self, message: str):
        """记录警告"""
        self.warnings.append(message)
        print(f"⚠️  {message}")
    
    def log_success(self, message: str):
        """记录成功"""
        self.passed_checks.append(message)
        print(f"✅ {message}")
    
    def check_file_structure(self):
        """检查文件结构"""
        print("\n📁 检查项目文件结构...")
        
        required_files = [
            "README.md",
            "pyproject.toml",
            "docker-compose.yml",
            "docker-compose.prod.yml",
            "Dockerfile",
            "Dockerfile.prod",
            ".env.example",
            "alembic.ini",
            "evoflow/__init__.py",
            "evoflow/main.py",
            "evoflow/config.py",
            "evoflow/database.py",
            "evoflow/celery_app.py",
        ]
        
        required_dirs = [
            "evoflow",
            "evoflow/models",
            "evoflow/schemas", 
            "evoflow/api",
            "evoflow/api/v1",
            "evoflow/agents",
            "evoflow/workflow",
            "evoflow/tasks",
            "evoflow/utils",
            "scripts",
            "examples",
            "tests",
            "alembic",
            "alembic/versions",
            "nginx",
        ]
        
        # 检查必需文件
        missing_files = []
        for file_path in required_files:
            if not (self.project_root / file_path).exists():
                missing_files.append(file_path)
        
        if missing_files:
            self.log_error(f"缺少必需文件: {', '.join(missing_files)}")
        else:
            self.log_success("所有必需文件存在")
        
        # 检查必需目录
        missing_dirs = []
        for dir_path in required_dirs:
            if not (self.project_root / dir_path).is_dir():
                missing_dirs.append(dir_path)
        
        if missing_dirs:
            self.log_error(f"缺少必需目录: {', '.join(missing_dirs)}")
        else:
            self.log_success("所有必需目录存在")
    
    def check_python_imports(self):
        """检查Python导入"""
        print("\n🐍 检查Python模块导入...")
        
        try:
            # 检查主要模块
            import evoflow
            self.log_success("evoflow模块导入成功")
            
            from evoflow.config import settings
            self.log_success("配置模块导入成功")
            
            from evoflow.database import Base
            self.log_success("数据库模块导入成功")
            
            from evoflow.models import User, Workflow, Agent
            self.log_success("数据模型导入成功")
            
            from evoflow.agents import BaseAgent, WebSearchAgent, TextWritingAgent
            self.log_success("Agent模块导入成功")
            
            from evoflow.workflow import WorkflowEngine, WorkflowDAG
            self.log_success("工作流引擎导入成功")
            
        except ImportError as e:
            self.log_error(f"模块导入失败: {e}")
    
    def check_configuration(self):
        """检查配置文件"""
        print("\n🔧 检查配置文件...")
        
        # 检查pyproject.toml
        pyproject_path = self.project_root / "pyproject.toml"
        if pyproject_path.exists():
            try:
                import tomli
                with open(pyproject_path, 'rb') as f:
                    config = tomli.load(f)
                
                if 'project' in config:
                    self.log_success("pyproject.toml格式正确")
                else:
                    self.log_error("pyproject.toml缺少project配置")
            except Exception as e:
                self.log_error(f"pyproject.toml解析失败: {e}")
        
        # 检查环境变量示例
        env_example_path = self.project_root / ".env.example"
        if env_example_path.exists():
            with open(env_example_path, 'r') as f:
                content = f.read()
                required_vars = [
                    "DATABASE_URL",
                    "REDIS_URL",
                    "DEEPSEEK_API_KEY",
                    "SECRET_KEY"
                ]
                
                missing_vars = [var for var in required_vars if var not in content]
                if missing_vars:
                    self.log_warning(f".env.example缺少变量: {', '.join(missing_vars)}")
                else:
                    self.log_success(".env.example包含所有必需变量")
    
    def check_docker_config(self):
        """检查Docker配置"""
        print("\n🐳 检查Docker配置...")
        
        # 检查docker-compose.yml
        compose_path = self.project_root / "docker-compose.yml"
        if compose_path.exists():
            try:
                import yaml
                with open(compose_path, 'r') as f:
                    compose_config = yaml.safe_load(f)
                
                required_services = ['postgres', 'redis', 'backend']
                services = compose_config.get('services', {})
                
                missing_services = [svc for svc in required_services if svc not in services]
                if missing_services:
                    self.log_error(f"docker-compose.yml缺少服务: {', '.join(missing_services)}")
                else:
                    self.log_success("docker-compose.yml包含所有必需服务")
                    
            except Exception as e:
                self.log_error(f"docker-compose.yml解析失败: {e}")
        
        # 检查Dockerfile
        dockerfile_path = self.project_root / "Dockerfile"
        if dockerfile_path.exists():
            with open(dockerfile_path, 'r') as f:
                content = f.read()
                if 'FROM python:3.11' in content:
                    self.log_success("Dockerfile使用正确的Python版本")
                else:
                    self.log_warning("Dockerfile可能使用了错误的Python版本")
    
    def check_database_migrations(self):
        """检查数据库迁移"""
        print("\n🗄️  检查数据库迁移...")
        
        alembic_dir = self.project_root / "alembic"
        versions_dir = alembic_dir / "versions"
        
        if not alembic_dir.exists():
            self.log_error("alembic目录不存在")
            return
        
        if not versions_dir.exists():
            self.log_error("alembic/versions目录不存在")
            return
        
        # 检查是否有迁移文件
        migration_files = list(versions_dir.glob("*.py"))
        if migration_files:
            self.log_success(f"找到 {len(migration_files)} 个迁移文件")
        else:
            self.log_warning("没有找到数据库迁移文件")
        
        # 检查alembic.ini
        alembic_ini = self.project_root / "alembic.ini"
        if alembic_ini.exists():
            self.log_success("alembic.ini配置文件存在")
        else:
            self.log_error("alembic.ini配置文件不存在")
    
    def check_scripts(self):
        """检查脚本文件"""
        print("\n📜 检查脚本文件...")
        
        scripts_dir = self.project_root / "scripts"
        required_scripts = [
            "start.sh",
            "stop.sh", 
            "dev.sh",
            "deploy.sh",
            "check_setup.py",
            "test_api.py",
            "monitor.py",
            "init_data.py",
            "validate_project.py"
        ]
        
        missing_scripts = []
        for script in required_scripts:
            script_path = scripts_dir / script
            if not script_path.exists():
                missing_scripts.append(script)
            elif script.endswith('.sh'):
                # 检查shell脚本是否有执行权限
                if not os.access(script_path, os.X_OK):
                    self.log_warning(f"脚本 {script} 没有执行权限")
        
        if missing_scripts:
            self.log_error(f"缺少脚本文件: {', '.join(missing_scripts)}")
        else:
            self.log_success("所有必需脚本文件存在")
    
    def check_examples(self):
        """检查示例文件"""
        print("\n📚 检查示例文件...")
        
        examples_dir = self.project_root / "examples"
        if not examples_dir.exists():
            self.log_error("examples目录不存在")
            return
        
        example_files = list(examples_dir.glob("*.py"))
        if example_files:
            self.log_success(f"找到 {len(example_files)} 个示例文件")
        else:
            self.log_warning("没有找到示例文件")
    
    def check_tests(self):
        """检查测试文件"""
        print("\n🧪 检查测试文件...")
        
        tests_dir = self.project_root / "tests"
        if not tests_dir.exists():
            self.log_error("tests目录不存在")
            return
        
        test_files = list(tests_dir.glob("test_*.py"))
        if test_files:
            self.log_success(f"找到 {len(test_files)} 个测试文件")
        else:
            self.log_warning("没有找到测试文件")
    
    async def run_syntax_check(self):
        """运行语法检查"""
        print("\n🔍 运行Python语法检查...")
        
        try:
            # 检查主要Python文件的语法
            python_files = [
                "evoflow/main.py",
                "evoflow/config.py",
                "evoflow/database.py",
                "scripts/check_setup.py",
                "scripts/test_api.py"
            ]
            
            for file_path in python_files:
                full_path = self.project_root / file_path
                if full_path.exists():
                    result = subprocess.run(
                        [sys.executable, "-m", "py_compile", str(full_path)],
                        capture_output=True,
                        text=True
                    )
                    
                    if result.returncode == 0:
                        self.log_success(f"{file_path} 语法正确")
                    else:
                        self.log_error(f"{file_path} 语法错误: {result.stderr}")
                        
        except Exception as e:
            self.log_error(f"语法检查失败: {e}")
    
    def generate_report(self):
        """生成验证报告"""
        print("\n" + "="*60)
        print("📊 项目验证报告")
        print("="*60)
        
        total_checks = len(self.passed_checks) + len(self.warnings) + len(self.errors)
        
        print(f"\n✅ 通过检查: {len(self.passed_checks)}")
        print(f"⚠️  警告: {len(self.warnings)}")
        print(f"❌ 错误: {len(self.errors)}")
        print(f"📊 总计: {total_checks}")
        
        if self.warnings:
            print(f"\n⚠️  警告详情:")
            for warning in self.warnings:
                print(f"   • {warning}")
        
        if self.errors:
            print(f"\n❌ 错误详情:")
            for error in self.errors:
                print(f"   • {error}")
        
        print(f"\n{'='*60}")
        
        if len(self.errors) == 0:
            print("🎉 项目验证通过！所有检查都成功完成。")
            print("\n下一步:")
            print("   1. 运行: ./scripts/start.sh")
            print("   2. 访问: http://localhost:8000/docs")
            print("   3. 测试: python scripts/test_api.py")
            return True
        else:
            print("❌ 项目验证失败！请修复上述错误后重新验证。")
            return False
    
    async def run_all_checks(self):
        """运行所有检查"""
        print("🔍 开始EvoFlow项目完整性验证")
        print("="*60)
        
        # 运行各项检查
        self.check_file_structure()
        self.check_python_imports()
        self.check_configuration()
        self.check_docker_config()
        self.check_database_migrations()
        self.check_scripts()
        self.check_examples()
        self.check_tests()
        await self.run_syntax_check()
        
        # 生成报告
        return self.generate_report()


async def main():
    """主函数"""
    validator = ProjectValidator()
    success = await validator.run_all_checks()
    
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
