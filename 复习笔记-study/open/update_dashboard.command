#!/bin/zsh
set -e
SCRIPT_DIR="${0:A:h}"
STUDY_DIR="${SCRIPT_DIR:h}"
python3 "/home/sandbox-agent/workspace/weekly-reports/study-assistant-skills/study-assistant/scripts/build_dashboard.py" "$STUDY_DIR"
echo
echo "仪表盘已更新：$SCRIPT_DIR/dashboard.html"
echo "按任意键关闭..."
read -k 1
