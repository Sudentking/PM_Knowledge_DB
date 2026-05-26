@echo off
echo Starting Product Manager Knowledge DB Scheduler...
cd /d "%~dp0"
python scripts/scheduler.py
pause
