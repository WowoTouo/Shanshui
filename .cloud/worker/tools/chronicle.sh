#!/bin/bash
# 基石日志生成器（CHRONICLE）— 零 token，零改 worker
# 职责：从 worker.log 提取关键事件（含时间戳）→ 追加 /home/agent/CHRONICLE.md → git 同步
# 与 FOUNDATION（协议层）/ SIGNAL（机读信令层）互补：本文件是【事实档案层】
# 运行：cron 每日 0 7 * * * + 可手动
LOG=/home/agent/logs/worker.log
CHRON=/home/agent/CHRONICLE.md
STATE=/home/agent/logs/chronicle_cursor.txt
REPO=/home/agent/Shanshui
KEYWORDS='TASK START|TASK LLM OK|TASK DONE|AUTO SPAWN|AUTO STALL|CLEANUP|QUOTA|FATAL|ERROR|MAIL|PROPOSAL|RESET|DEPLOY|RESTART'

LAST=0; [ -f "$STATE" ] && LAST=$(cat "$STATE" 2>/dev/null)
TOTAL=$(wc -l < "$LOG" 2>/dev/null || echo 0)
[ "$TOTAL" -le "$LAST" ] && exit 0   # 无新日志行

awk -v s="$LAST" -v k="$KEYWORDS" 'NR>s && $0 ~ k {print}' "$LOG" | head -80 > /tmp/chr_new.txt
if [ -s /tmp/chr_new.txt ]; then
  TODAY=$(date +%F)
  {
    echo ""
    echo "## $TODAY"
    while IFS= read -r line; do
      ts=$(echo "$line" | awk '{print $1" "$2}')
      rest=$(echo "$line" | cut -d' ' -f3-)
      echo "- $ts | $rest"
    done < /tmp/chr_new.txt
  } >> "$CHRON"
  echo "CHRONICLE: +$(wc -l < /tmp/chr_new.txt) entries"
else
  echo "CHRONICLE: no new key events"
fi
echo "$TOTAL" > "$STATE"

# 同步进 git 仓库并推送（agent 凭证已有 Gitee）
if [ -d "$REPO/coordination" ]; then
  cp "$CHRON" "$REPO/coordination/CHRONICLE.md"
  cd "$REPO" && git add coordination/CHRONICLE.md && git commit -m "CHRONICLE: $(date +%F) 日志追加" -q && git push gitee main -q 2>/dev/null && echo "CHRONICLE pushed" || echo "CHRONICLE commit ok (push skipped)"
fi
