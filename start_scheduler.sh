#!/bin/bash
echo "Starting Product Manager Knowledge DB Scheduler..."
cd "$(dirname "$0")"
python3 scripts/scheduler.py
