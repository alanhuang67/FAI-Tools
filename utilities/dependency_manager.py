import subprocess
import sys

def install_dependencies():
    required = ['pandas', 'openpyxl']
    for module in required:
        try:
            __import__(module)
        except ImportError:
            print(f"正在安装缺失的依赖: {module} …")
            subprocess.check_call([
                sys.executable, "-m", "pip", "install",
                "--disable-pip-version-check", module
            ])
