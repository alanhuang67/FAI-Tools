import subprocess
import sys
import os
import pip

def install_dependencies():
    """安装所需的依赖包"""
    required = ['pandas', 'openpyxl']
    
    # 设置pip安装选项
    pip_options = [
        "--index-url", "https://pypi.tuna.tsinghua.edu.cn/simple",
        "--trusted-host", "pypi.tuna.tsinghua.edu.cn",
        "--disable-pip-version-check",
        "--no-cache-dir"  # 禁用缓存
    ]
    
    for module in required:
        try:
            __import__(module)
            print(f"{module} 已安装，跳过...")
        except ImportError:
            print(f"正在安装缺失的依赖: {module}")
            try:
                # 使用subprocess运行pip命令
                cmd = [sys.executable, "-m", "pip", "install"] + pip_options + [module]
                result = subprocess.run(cmd, 
                                     capture_output=True, 
                                     text=True,
                                     env=dict(os.environ, PIP_DISABLE_PIP_VERSION_CHECK="1"))
                
                if result.returncode != 0:
                    print(f"安装 {module} 失败")
                    print("错误信息:", result.stderr)
                    return False
                else:
                    print(f"{module} 安装成功")
                    
            except Exception as e:
                print(f"安装过程出错: {str(e)}")
                return False
                
    return True
