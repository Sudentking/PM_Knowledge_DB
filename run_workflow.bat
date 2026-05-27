@echo off
chcp 65001 >nul
cd /d D:\code\Knowledge_DB

echo ======================================== >> logs\workflow_run.log
echo 运行时间: %date% %time% >> logs\workflow_run.log
echo ======================================== >> logs\workflow_run.log

python scripts/workflow.py --mode full >> logs\workflow_run.log 2>&1

echo. >> logs\workflow_run.log
echo 运行完成: %date% %time% >> logs\workflow_run.log
echo ======================================== >> logs\workflow_run.log
echo. >> logs\workflow_run.log
