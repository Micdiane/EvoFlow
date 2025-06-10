import subprocess
import os
import sys

def run_command(command):
    try:
        result = subprocess.run(command, shell=True, check=True, text=True, capture_output=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"错误: {e.stderr}")
        return None

def main():
    # 获取当前目录
    current_dir = os.getcwd()
    # 添加所有文件
    print("正在添加文件...")
    run_command("git add .")
    
    # 提交更改
    print("正在提交更改...")
    run_command('git commit -m "Initial commit"')
    
    # 尝试推送代码
    print("正在推送代码...")
    try:
        # 首先尝试拉取远程仓库
        run_command("git pull origin main --allow-unrelated-histories")
    except:
        print("拉取远程仓库失败，继续推送...")
    
    # 推送代码
    run_command("git push -u origin main")
    
    print("操作完成！")

if __name__ == "__main__":
    main() 