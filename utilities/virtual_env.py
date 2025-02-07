import os
import sys
import subprocess

def create_and_activate_venv():
    """创建并激活虚拟环境"""
    if sys.prefix == sys.base_prefix:
        venv_dir = os.path.join(os.path.dirname(__file__), "venv")
        if not os.path.exists(venv_dir):
            print("正在创建独立虚拟环境……")
            subprocess.check_call([sys.executable, "-m", "venv", venv_dir])
        if os.name == "nt":
            python_path = os.path.join(venv_dir, "Scripts", "python.exe")
        else:
            python_path = os.path.join(venv_dir, "bin", "python")
        print("切换至独立虚拟环境……")
        subprocess.check_call([python_path] + sys.argv)
        sys.exit(0)
