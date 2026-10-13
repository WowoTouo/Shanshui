#!/bin/bash
# 山水工程 AI Worker 每日摘要 + 邮件推送（cron 每天 06:00 由 agent 用户执行）
# 产出：/home/agent/logs/daily/YYYY-MM-DD.md，并以 md 格式邮件推送（正文 text/markdown + .md 附件）到 .env 里 MAIL_TO 指定的邮箱
set -euo pipefail
YESTERDAY=$(date -d 'yesterday' '+%Y-%m-%d')
OUT_DIR="/home/agent/logs/daily"
mkdir -p "$OUT_DIR"

env_get() { grep -E "^$1=" /home/agent/.env 2>/dev/null | head -1 | cut -d= -f2- || true; }

# 找昨天的日志（轮转后的 .1 或当天文件）
LOG_SRC=""
for f in "/home/agent/logs/worker.log.1" "/home/agent/logs/worker.log"; do
    if [ -f "$f" ] && grep -q "$YESTERDAY" "$f" 2>/dev/null; then
        LOG_SRC="$f"
        break
    fi
done

OUT="$OUT_DIR/$YESTERDAY.md"
{
    echo "# 山水工程 AI Worker 日报 · $YESTERDAY"
    echo
    if [ -z "$LOG_SRC" ]; then
        echo "_昨天没有日志记录。_"
    else
        echo "## 任务统计"
        echo "- 开始任务：$(grep -c "TASK START" "$LOG_SRC" || true)"
        echo "- 完成任务：$(grep -c "TASK DONE" "$LOG_SRC" || true)"
        echo "- 报错次数：$(grep -c "ERROR" "$LOG_SRC" || true)"
        echo
        echo "## Token 消耗"
        grep "TASK LLM OK" "$LOG_SRC" | sed 's/.*tokens=/tokens=/' || echo "_无_"
        echo
        echo "## 任务清单"
        grep -E "TASK (START|DONE|ERROR)" "$LOG_SRC" | sed "s/\[$YESTERDAY/[日期/;s/^/    /" || true
    fi
} > "$OUT"

echo "$(date '+%Y-%m-%d %H:%M:%S') daily summary -> $OUT" >> "/home/agent/logs/worker.log"

# ===== 飞书机器人推送（.env 填 FEISHU_WEBHOOK 即启用）=====
FEISHU=$(env_get FEISHU_WEBHOOK)
if [ -n "$FEISHU" ]; then
    FEISHU_TEXT=$(printf '山水工程 AI 日报 %s\n%s' "$YESTERDAY" "$(head -c 1500 "$OUT")")
    if command -v jq >/dev/null 2>&1; then
        JSON=$(jq -Rn --arg t "$FEISHU_TEXT" '{msg_type:"text",content:{text:$t}}')
        CODE=$(curl -s -o /dev/null -w '%{http_code}' --max-time 15 -X POST "$FEISHU" \
            -H 'Content-Type: application/json' -d "$JSON")
    else
        CODE="no-jq"
    fi
    if [ "$CODE" = "200" ]; then
        echo "$(date '+%Y-%m-%d %H:%M:%S') feishu pushed OK" >> "/home/agent/logs/worker.log"
    else
        echo "$(date '+%Y-%m-%d %H:%M:%S') feishu FAILED (http=$CODE)" >> "/home/agent/logs/worker.log"
    fi
fi

# ===== 邮件推送（凭证齐全 + msmtprc 就绪才发；双收件人 MAIL_TO/MAIL_TO2 同时发）=====
# 铁律（2026-10-13 用户指令）：每一次发邮件都用 md 文件——正文 text/markdown + 附件日报 .md 原件
MAIL_TO=$(env_get MAIL_TO)
MAIL_TO2=$(env_get MAIL_TO2)
MAIL_FROM=$(env_get MAIL_FROM)
MAIL_PASS=$(env_get MAIL_PASS)
RECIPIENTS=()
[ -n "$MAIL_TO" ] && RECIPIENTS+=("$MAIL_TO")
[ -n "$MAIL_TO2" ] && RECIPIENTS+=("$MAIL_TO2")
if [ ${#RECIPIENTS[@]} -gt 0 ] && [ -n "$MAIL_FROM" ] && [ -n "$MAIL_PASS" ] && [ -f /home/agent/.msmtprc ]; then
    TO_HDR="$MAIL_TO"
    [ -n "$MAIL_TO2" ] && TO_HDR="$TO_HDR, $MAIL_TO2"
    BOUNDARY="shanshui-$(date +%s)-$$"
    TMPF=$(mktemp /tmp/ss-mail.XXXXXX)
    ATTF=$(mktemp /tmp/ss-mail-att.XXXXXX)
    base64 "$OUT" > "$ATTF"
    {
        printf 'To: %s\n' "$TO_HDR"
        printf 'From: %s\n' "$MAIL_FROM"
        printf 'Subject: [山水工程] AI 日报 %s\n' "$YESTERDAY"
        printf 'MIME-Version: 1.0\n'
        printf 'Content-Type: multipart/mixed; boundary="%s"\n\n' "$BOUNDARY"
        printf -- '--%s\n' "$BOUNDARY"
        printf 'Content-Type: text/markdown; charset=UTF-8\n\n'
        cat "$OUT"
        printf '\n--%s\n' "$BOUNDARY"
        printf 'Content-Type: text/markdown; charset=UTF-8; name="%s.md"\n' "$YESTERDAY"
        printf 'Content-Transfer-Encoding: base64\n'
        printf 'Content-Disposition: attachment; filename="%s.md"\n\n' "$YESTERDAY"
        cat "$ATTF"
        printf -- '--%s--\n' "$BOUNDARY"
    } > "$TMPF"
    if msmtp "${RECIPIENTS[@]}" < "$TMPF" 2>>/home/agent/logs/worker.log; then
        echo "$(date '+%Y-%m-%d %H:%M:%S') mail(md) sent to ${RECIPIENTS[*]}" >> "/home/agent/logs/worker.log"
    else
        echo "$(date '+%Y-%m-%d %H:%M:%S') mail FAILED (see msmtp.log)" >> "/home/agent/logs/worker.log"
    fi
    rm -f "$TMPF" "$ATTF"
else
    echo "$(date '+%Y-%m-%d %H:%M:%S') mail skipped (凭证未填全)" >> "/home/agent/logs/worker.log"
fi
