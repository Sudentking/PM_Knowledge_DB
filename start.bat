@echo off
chcp 65001 >nul
echo ========================================
echo 产品经理知识库 - 快速启动
echo ========================================
echo.

echo [1/3] 检查Python环境...
python --version
if errorlevel 1 (
    echo 错误: Python未安装或未配置环境变量
    pause
    exit /b 1
)

echo.
echo [2/3] 检查依赖包...
pip show requests beautifulsoup4 openai gitpython >nul 2>&1
if errorlevel 1 (
    echo 正在安装依赖包...
    pip install -r requirements.txt
)

echo.
echo [3/3] 运行系统测试...
python scripts/test_system.py

echo.
echo ========================================
echo 配置说明:
echo 1. 设置OPENAI_API_KEY环境变量
echo 2. 配置GitHub远程仓库
echo 3. 运行: python scripts/workflow.py
echo ========================================
echo.
pause
