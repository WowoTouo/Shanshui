#!/bin/bash
# 山水工程 磁盘告警：/ 使用率 >85% 时推送飞书 + 记日志 + 生成 md 告警报告（凭证不全只记日志）
# 由 agent crontab 每 6 小时执行：0 */6 * * *
set -u
THRESHOLD=85
TS=$(date '+%Y-%m-%d %H:%M:%S')
USE=$(df --output=pcent / | tail -1 | tr -dc '0-9')

if [ "$USE" -lt "$THRESHOLD" ]; then
    echo "$TS disk ok (${USE}%)" >> /home/agent/logs/worker.log
    exit 0
fi

MSG="[山水工程] 磁盘告警：/ 使用率 ${USE}%（阈值 ${THRESHOLD}%）
$(df -h / | tail -1)
$(du -sh /home/agent 2>/dev/null || true)"
echo "$TS DISK ALERT ${USE}%" >> /home/agent/logs/worker.log

# 同步产出 md 告警报告（2026-10-13 用户指令：生成的报告日志尽可能用 md 格式）
ALERT_MD="/home/agent/logs/alerts/$(date '+%Y-%m').md"
mkdir -p /home/agent/logs/alerts
[ -f "$ALERT_MD" ] || printf '# 山水工程 告警记录 · %s\n' "$(date '+%Y-%m')" > "$ALERT_MD"
{
    printf '\n## %s 磁盘使用率 %s%%\n\n' "$TS" "$USE"
    printf -- '- 阈值：%s%%\n' "$THRESHOLD"
    printf -- '- 分区现状：`%s`\n' "$(df -h / | tail -1)"
    printf -- '- agent 目录占用：`%s`\n' "$(du -sh /home/agent 2>/dev/null || echo n/a)"
    printf -- '- 处置建议：清理 logs 轮转归档，或考虑扩容磁盘\n'
} >> "$ALERT_MD"

FEISHU=$(grep -E '^FEISHU_WEBHOOK=' /home/agent/.env 2>/dev/null | head -1 | cut -d= -f2- || true)
if [ -n "$FEISHU" ] && command -v jq >/dev/null 2>&1; then
    curl -s -o /dev/null --max-time 15 -X POST "$FEISHU" \
        -H 'Content-Type: application/json' \
        -d "$(jq -Rn --arg t "$MSG" '{msg_type:"text",content:{text:$t}}')" \
        && echo "$TS feishu disk-alert pushed" >> /home/agent/logs/worker.log \
        || echo "$TS feishu disk-alert FAILED" >> /home/agent/logs/worker.log
fi
