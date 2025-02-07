@echo off
@chcp 65001 >nul

REM 启用虚拟终端支持 ANSI 转义序列
REG ADD HKCU\Console /v VirtualTerminalLevel /t REG_DWORD /d 1 /f >nul

REM 切换到脚本所在目录
cd /d %~dp0

REM 设置颜色为 RGB #FF0072
echo [38;2;255;0;114m启动程序中...[0m

REM 检查虚拟环境是否存在
if not exist "venv" (
    echo 正在创建虚拟环境...
    python -m venv venv
)

REM 激活虚拟环境
call venv\Scripts\activate

REM 设置环境变量禁用 pip 版本检查
set PIP_DISABLE_PIP_VERSION_CHECK=1

REM 检查并安装依赖
echo 正在检查依赖...
pip list | findstr pandas >nul
if errorlevel 1 (
    echo 检测到缺失依赖，正在安装依赖...
    pip install pandas openpyxl --disable-pip-version-check
) else (
    echo [38;2;0;255;0m依赖已满足，跳过安装...[0m
)

REM 启动 main.py
echo [38;2;0;191;255m正在启动程序...[0m
python main.py

REM 程序执行完毕后保留窗口
pause
