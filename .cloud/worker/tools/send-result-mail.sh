#!/bin/bash
# 山水工程 · result 邮件推送（md 格式铁律：正文 text/markdown + .md 附件）
# 用法: send-result-mail.sh <邮件主题> <result md 文件路径>
# 由 agent 用户执行；复用 summary.sh v4 已验证的 multipart/mixed 结构
set -uo pipefail
SUBJECT="$1"
MD="$2"
[ -f "$MD" ] || { echo "NO_MD: $MD 不存在"; exit 1; }
env_get() { grep -E "^$1=" /home/agent/.env 2>/dev/null | head -1 | cut -d= -f2- || true; }
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
    base64 "$MD" > "$ATTF"
    {
        printf 'To: %s\n' "$TO_HDR"
        printf 'From: %s\n' "$MAIL_FROM"
        printf 'Subject: %s\n' "$SUBJECT"
        printf 'MIME-Version: 1.0\n'
        printf 'Content-Type: multipart/mixed; boundary="%s"\n\n' "$BOUNDARY"
        printf -- '--%s\n' "$BOUNDARY"
        printf 'Content-Type: text/markdown; charset=UTF-8\n\n'
        cat "$MD"
        printf '\n--%s\n' "$BOUNDARY"
        printf 'Content-Type: text/markdown; charset=UTF-8; name="%s"\n' "$(basename "$MD")"
        printf 'Content-Transfer-Encoding: base64\n'
        printf 'Content-Disposition: attachment; filename="%s"\n\n' "$(basename "$MD")"
        cat "$ATTF"
        printf -- '--%s--\n' "$BOUNDARY"
    } > "$TMPF"
    if msmtp "${RECIPIENTS[@]}" < "$TMPF" 2>>/home/agent/logs/worker.log; then
        echo "$(date '+%Y-%m-%d %H:%M:%S') mail(md) sent: $SUBJECT -> ${RECIPIENTS[*]}" >> "/home/agent/logs/worker.log"
        echo "MAIL_SENT"
    else
        echo "$(date '+%Y-%m-%d %H:%M:%S') mail FAILED: $SUBJECT (see msmtp.log)" >> "/home/agent/logs/worker.log"
        echo "MAIL_FAILED"
    fi
    rm -f "$TMPF" "$ATTF"
else
    echo "$(date '+%Y-%m-%d %H:%M:%S') mail skipped (凭证未填全)" >> "/home/agent/logs/worker.log"
    echo "MAIL_SKIPPED"
fi
