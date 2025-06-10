#!/usr/bin/env python3
"""
EvoFlow 项目设置检查脚本
"""
import os
import sys
import subprocess
from pathlib import Path


def check_python_version():
    """检查Python版本"""
    print("🐍 检查Python版本...")
    version = sys.version_info
    if version.major == 3 and version.minor >= 11:
        print(f"✅ Python版本: {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"❌ Python版本过低: {version.major}.{version.minor}.{version.micro}")
        print("   需要Python 3.11或更高版本")
        return False


def check_docker():
    """检查Docker是否可用"""
    print("\n🐳 检查Docker...")
    try:
        result = subprocess.run(["docker", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Docker版本: {result.stdout.strip()}")
            return True
        else:
            print("❌ Docker未安装或不可用")
            return False
    except FileNotFoundError:
        print("❌ Docker未安装")
        return False


def check_docker_compose():
    """检查Docker Compose是否可用"""
    print("\n📦 检查Docker Compose...")
    try:
        result = subprocess.run(["docker-compose", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Docker Compose版本: {result.stdout.strip()}")
            return True
        else:
            # 尝试新版本的命令
            result = subprocess.run(["docker", "compose", "version"], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ Docker Compose版本: {result.stdout.strip()}")
                return True
            else:
                print("❌ Docker Compose未安装或不可用")
                return False
    except FileNotFoundError:
        print("❌ Docker Compose未安装")
        return False


def check_uv():
    """检查uv包管理器"""
    print("\n📦 检查uv包管理器...")
    try:
        result = subprocess.run(["uv", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ uv版本: {result.stdout.strip()}")
            return True
        else:
            print("❌ uv未安装")
            print("   安装命令: pip install uv")
            return False
    except FileNotFoundError:
        print("❌ uv未安装")
        print("   安装命令: pip install uv")
        return False


def check_env_file():
    """检查环境变量文件"""
    print("\n🔧 检查环境配置...")
    env_file = Path(".env")
    if env_file.exists():
        print("✅ .env文件存在")
        
        # 检查关键配置
        with open(env_file, 'r') as f:
            content = f.read()
            
        required_vars = [
            "DATABASE_URL",
            "REDIS_URL", 
            "DEEPSEEK_API_KEY",
            "SECRET_KEY"
        ]
        
        missing_vars = []
        for var in required_vars:
            if var not in content:
                missing_vars.append(var)
        
        if missing_vars:
            print(f"⚠️  缺少环境变量: {', '.join(missing_vars)}")
            return False
        else:
            print("✅ 环境变量配置完整")
            return True
    else:
        print("❌ .env文件不存在")
        print("   请复制.env.example到.env并配置相应的值")
        return False


def check_project_structure():
    """检查项目结构"""
    print("\n📁 检查项目结构...")
    
    required_dirs = [
        "evoflow",
        "evoflow/models",
        "evoflow/api",
        "evoflow/agents", 
        "evoflow/workflow",
        "scripts",
        "examples"
    ]
    
    required_files = [
        "pyproject.toml",
        "docker-compose.yml",
        "Dockerfile",
        "evoflow/main.py",
        "evoflow/config.py"
    ]
    
    missing_items = []
    
    for dir_path in required_dirs:
        if not Path(dir_path).is_dir():
            missing_items.append(f"目录: {dir_path}")
    
    for file_path in required_files:
        if not Path(file_path).is_file():
            missing_items.append(f"文件: {file_path}")
    
    if missing_items:
        print("❌ 项目结构不完整:")
        for item in missing_items:
            print(f"   缺少 {item}")
        return False
    else:
        print("✅ 项目结构完整")
        return True


def check_dependencies():
    """检查Python依赖"""
    print("\n📚 检查Python依赖...")
    
    if not Path("pyproject.toml").exists():
        print("❌ pyproject.toml文件不存在")
        return False
    
    try:
        # 尝试导入关键模块
        import fastapi
        import sqlalchemy
        import redis
        import celery
        print("✅ 核心依赖已安装")
        return True
    except ImportError as e:
        print(f"❌ 缺少依赖: {e}")
        print("   运行: uv pip install -e '.[dev]'")
        return False


def main():
    """主检查函数"""
    print("🚀 EvoFlow 项目设置检查")
    print("=" * 50)
    
    checks = [
        ("Python版本", check_python_version),
        ("Docker", check_docker),
        ("Docker Compose", check_docker_compose),
        ("uv包管理器", check_uv),
        ("环境配置", check_env_file),
        ("项目结构", check_project_structure),
        ("Python依赖", check_dependencies)
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ {name}检查失败: {e}")
            results.append((name, False))
    
    print("\n" + "=" * 50)
    print("📊 检查结果汇总:")
    
    passed = 0
    total = len(results)
    
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"   {name}: {status}")
        if result:
            passed += 1
    
    print(f"\n总计: {passed}/{total} 项检查通过")
    
    if passed == total:
        print("\n🎉 所有检查通过！项目已准备就绪。")
        print("\n下一步:")
        print("   1. 启动服务: ./scripts/start.sh")
        print("   2. 或开发模式: ./scripts/dev.sh")
        print("   3. 访问API文档: http://localhost:8000/docs")
    else:
        print(f"\n⚠️  还有 {total - passed} 项需要修复。")
        print("请根据上述提示解决问题后重新运行检查。")
        sys.exit(1)


if __name__ == "__main__":
    main()
