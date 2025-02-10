import os
import sys
import subprocess

def create_and_activate_venv():
    """创建并激活虚拟环境"""
    if sys.prefix == sys.base_prefix:
        # 获取当前脚本的绝对路径
        current_file = os.path.abspath(__file__)
        # 获取项目根目录
        base_dir = os.path.dirname(os.path.dirname(current_file))
        # 在项目根目录下创建venv文件夹
        venv_dir = os.path.join(base_dir, "venv")
        
        if not os.path.exists(venv_dir):
            print("正在创建独立虚拟环境...")
            try:
                subprocess.check_call([sys.executable, "-m", "venv", venv_dir])
            except subprocess.CalledProcessError:
                print("创建虚拟环境失败")
                return False
        
        if os.name == "nt":
            python_path = os.path.join(venv_dir, "Scripts", "python.exe")
        else:
            python_path = os.path.join(venv_dir, "bin", "python")
            
        if os.path.exists(python_path):
            print("切换至独立虚拟环境...")
            try:
                subprocess.check_call([python_path] + sys.argv)
                sys.exit(0)
            except subprocess.CalledProcessError:
                print("切换虚拟环境失败")
                return False