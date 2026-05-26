"""定时任务调度模块"""

import os
import sys
import time
import signal
import argparse
from datetime import datetime
from pathlib import Path

import yaml

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.utils.logger import setup_logger
from scripts.workflow import KnowledgeWorkflow

class TaskScheduler:
    """任务调度器"""

    def __init__(self, config_path: str = "config/config.yaml"):
        """初始化调度器

        Args:
            config_path: 配置文件路径
        """
        # 加载配置
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)

        # 初始化日志
        self.logger = setup_logger(
            self.config.get('logging', {}).get('file', 'logs/crawler.log'),
            self.config.get('logging', {}).get('level', 'INFO')
        )

        # 调度配置
        schedule_config = self.config.get('schedule', {})
        self.enabled = schedule_config.get('enabled', True)
        self.cron_expression = schedule_config.get('cron', '0 2 * * *')
        self.timezone = schedule_config.get('timezone', 'Asia/Shanghai')

        # 工作流
        self.workflow = KnowledgeWorkflow(config_path)

        # 运行状态
        self.running = True

        # 注册信号处理
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """信号处理器

        Args:
            signum: 信号编号
            frame: 栈帧
        """
        self.logger.info(f"收到信号 {signum}，正在停止...")
        self.running = False

    def _parse_cron(self, cron_expr: str) -> tuple:
        """解析cron表达式

        Args:
            cron_expr: cron表达式

        Returns:
            (minute, hour, day, month, weekday)
        """
        parts = cron_expr.split()
        if len(parts) != 5:
            raise ValueError(f"无效的cron表达式: {cron_expr}")

        minute, hour, day, month, weekday = parts
        return minute, hour, day, month, weekday

    def _should_run_now(self) -> bool:
        """检查是否应该运行

        Returns:
            是否应该运行
        """
        try:
            minute, hour, day, month, weekday = self._parse_cron(self.cron_expression)

            now = datetime.now()

            # 检查各字段
            if minute != '*' and now.minute != int(minute):
                return False
            if hour != '*' and now.hour != int(hour):
                return False
            if day != '*' and now.day != int(day):
                return False
            if month != '*' and now.month != int(month):
                return False
            if weekday != '*' and now.weekday() != int(weekday):
                return False

            return True
        except Exception as e:
            self.logger.error(f"解析cron表达式失败: {e}")
            return False

    def _get_next_run_time(self) -> datetime:
        """获取下次运行时间

        Returns:
            下次运行时间
        """
        try:
            minute, hour, day, month, weekday = self._parse_cron(self.cron_expression)

            now = datetime.now()

            # 简单实现：假设是每天定时任务
            if hour != '*' and minute != '*':
                next_run = now.replace(hour=int(hour), minute=int(minute), second=0, microsecond=0)
                if next_run <= now:
                    next_run = next_run.replace(day=now.day + 1)
                return next_run

            # 默认1小时后
            from datetime import timedelta
            return now + timedelta(hours=1)
        except Exception as e:
            self.logger.error(f"计算下次运行时间失败: {e}")
            from datetime import timedelta
            return datetime.now() + timedelta(hours=1)

    def run_once(self):
        """执行一次任务"""
        self.logger.info("开始执行定时任务")
        try:
            result = self.workflow.run_full_workflow()
            self.logger.info(f"任务执行完成: {result}")
        except Exception as e:
            self.logger.error(f"任务执行失败: {e}")

    def run_loop(self):
        """循环运行任务"""
        self.logger.info("启动定时任务调度器")
        self.logger.info(f"Cron表达式: {self.cron_expression}")
        self.logger.info(f"时区: {self.timezone}")

        while self.running:
            try:
                # 检查是否应该运行
                if self._should_run_now():
                    self.run_once()

                # 计算下次运行时间
                next_run = self._get_next_run_time()
                self.logger.info(f"下次运行时间: {next_run}")

                # 等待到下次运行时间
                while self.running and datetime.now() < next_run:
                    time.sleep(60)  # 每分钟检查一次

            except Exception as e:
                self.logger.error(f"调度器错误: {e}")
                time.sleep(60)

        self.logger.info("定时任务调度器已停止")

    def stop(self):
        """停止调度器"""
        self.running = False


def create_startup_script():
    """创建启动脚本"""
    # Windows批处理脚本
    bat_content = """@echo off
echo Starting Product Manager Knowledge DB Scheduler...
cd /d "%~dp0"
python scripts/scheduler.py
pause
"""

    bat_path = Path("start_scheduler.bat")
    with open(bat_path, 'w', encoding='utf-8') as f:
        f.write(bat_content)

    # Linux shell脚本
    sh_content = """#!/bin/bash
echo "Starting Product Manager Knowledge DB Scheduler..."
cd "$(dirname "$0")"
python3 scripts/scheduler.py
"""

    sh_path = Path("start_scheduler.sh")
    with open(sh_path, 'w', encoding='utf-8') as f:
        f.write(sh_content)

    # 添加执行权限
    try:
        import stat
        sh_path.chmod(sh_path.stat().st_mode | stat.S_IEXEC)
    except:
        pass

    print(f"已创建启动脚本:")
    print(f"  Windows: {bat_path}")
    print(f"  Linux/Mac: {sh_path}")


def create_windows_task():
    """创建Windows任务计划"""
    task_name = "ProductManagerKnowledgeDB"
    script_path = os.path.abspath("scripts/scheduler.py")
    python_path = sys.executable

    # 创建XML任务定义
    xml_content = f"""<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Description>产品经理知识库定时任务</Description>
  </RegistrationInfo>
  <Triggers>
    <CalendarTrigger>
      <StartBoundary>2026-01-01T02:00:00</StartBoundary>
      <Enabled>true</Enabled>
      <ScheduleByDay>
        <DaysInterval>1</DaysInterval>
      </ScheduleByDay>
    </CalendarTrigger>
  </Triggers>
  <Principals>
    <Principal id="Author">
      <LogonType>InteractiveToken</LogonType>
      <RunLevel>LeastPrivilege</RunLevel>
    </Principal>
  </Principals>
  <Settings>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <AllowHardTerminate>true</AllowHardTerminate>
    <StartWhenAvailable>true</StartWhenAvailable>
    <RunOnlyIfNetworkAvailable>true</RunOnlyIfNetworkAvailable>
    <IdleSettings>
      <StopOnIdleEnd>true</StopOnIdleEnd>
      <RestartOnIdle>false</RestartOnIdle>
    </IdleSettings>
    <AllowStartOnDemand>true</AllowStartOnDemand>
    <Enabled>true</Enabled>
    <Hidden>false</Hidden>
    <RunOnlyIfIdle>false</RunOnlyIfIdle>
    <WakeToRun>false</WakeToRun>
    <ExecutionTimeLimit>PT72H</ExecutionTimeLimit>
    <Priority>7</Priority>
  </Settings>
  <Actions Context="Author">
    <Exec>
      <Command>{python_path}</Command>
      <Arguments>{script_path}</Arguments>
      <WorkingDirectory>{os.path.dirname(script_path)}</WorkingDirectory>
    </Exec>
  </Actions>
</Task>
"""

    xml_path = Path("task_definition.xml")
    with open(xml_path, 'w', encoding='utf-16') as f:
        f.write(xml_content)

    print(f"已创建Windows任务定义: {xml_path}")
    print(f"\n请手动导入任务:")
    print(f"1. 打开任务计划程序")
    print(f"2. 点击'导入任务'")
    print(f"3. 选择 {xml_path}")
    print(f"4. 设置触发器为每天凌晨2点")
    print(f"5. 保存并启用任务")

    # 生成schtasks命令
    print(f"\n或使用命令行创建任务:")
    print(f'schtasks /create /tn "{task_name}" /tr "{python_path} {script_path}" /sc daily /st 02:00 /f')


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='定时任务调度器')
    parser.add_argument('--config', default='config/config.yaml', help='配置文件路径')
    parser.add_argument('--mode', choices=['run', 'loop', 'setup'],
                       default='loop', help='运行模式')
    parser.add_argument('--create-scripts', action='store_true', help='创建启动脚本')
    parser.add_argument('--create-task', action='store_true', help='创建Windows任务计划')

    args = parser.parse_args()

    if args.create_scripts:
        create_startup_script()
        return

    if args.create_task:
        create_windows_task()
        return

    # 创建调度器
    scheduler = TaskScheduler(args.config)

    if args.mode == 'run':
        # 执行一次
        scheduler.run_once()
    elif args.mode == 'loop':
        # 循环运行
        scheduler.run_loop()


if __name__ == "__main__":
    main()
