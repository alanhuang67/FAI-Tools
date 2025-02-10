import subprocess
import sys
import os

def install_dependencies():
    """安装所需的依赖包"""
    required = ['pandas', 'openpyxl']
    
    for module in required:
        try:
            __import__(module)
        except ImportError:
            print(f"正在安装缺失的依赖: {module}")
            try:
                # 使用清华镜像源安装
                subprocess.check_call([
                    sys.executable, 
                    "-m", 
                    "pip", 
                    "install",
                    "-i", 
                    "https://pypi.tuna.tsinghua.edu.cn/simple",
                    "--trusted-host", 
                    "pypi.tuna.tsinghua.edu.cn",
                    module
                ])
            except subprocess.CalledProcessError:
                print(f"安装 {module} 失败，请确保网络连接正常")
                return False
    return True