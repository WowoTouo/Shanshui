#!/bin/bash
# 山水工程 AI Worker 入口（systemd 调用）
set -euo pipefail
export PATH="/usr/local/bin:/usr/bin:/bin"
cd /home/agent/worker
exec /home/agent/venv312/bin/python worker.py
