#!/bin/bash

echo "========================================"
echo "产品经理知识库 - 快速启动"
echo "========================================"
echo ""

echo "[1/3] 检查Python环境..."
python3 --version
if [ $? -ne 0 ]; then
    echo "错误: Python未安装或未配置环境变量"
    exit 1
fi

echo ""
echo "[2/3] 检查依赖包..."
pip3 show requests beautifulsoup4 openai gitpython > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "正在安装依赖包..."
    pip3 install -r requirements.txt
fi

echo ""
echo "[3/3] 运行系统测试..."
python3 scripts/test_system.py

echo ""
echo "========================================"
echo "配置说明:"
echo "1. 设置OPENAI_API_KEY环境变量"
echo "2. 配置GitHub远程仓库"
echo "3. 运行: python3 scripts/workflow.py"
echo "========================================"
