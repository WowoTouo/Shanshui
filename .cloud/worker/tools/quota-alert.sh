#!/bin/bash
# 方舟额度估算监控（无 IAM AK/SK，推理 key 查不了余额）
# 口径：快照基准 4963479 @ 2026-10-13 19:0x（该刻余额已含此前全部消耗）
#   仅统计快照之后的新增 LLM 调用消耗，避免重复扣除：
#   - 解析 'TASK LLM OK ... tokens=<N>' 实际值累加；tokens=? 按 PER=8000 估算
#   - 余额 = 基准 - 累计新增估算消耗；精确值以火山控制台为准
LOG=/home/agent/logs/worker.log
QLOG=/home/agent/logs/quota.log
STATE=/home/agent/logs/quota_state.txt
BASE=4963479
PER=8000
THRESHOLD=1000000
TS=$(date '+%Y-%m-%d %H:%M:%S')

[ -f "$LOG" ] || { echo "[$TS] no worker.log, skip" >> "$QLOG"; exit 0; }

calls=$(grep -c 'TASK LLM OK' "$LOG" 2>/dev/null || echo 0)
actual=$(grep -oE 'tokens=[0-9]+' "$LOG" 2>/dev/null | grep -oE '[0-9]+' | awk '{s+=$1} END{print s+0}')
known=$(grep -oE 'tokens=[0-9]+' "$LOG" 2>/dev/null | wc -l)

if [ ! -f "$STATE" ]; then
  echo "$calls" > "$STATE"; echo "$actual" >> "$STATE"; echo "$BASE" >> "$STATE"; echo "$known" >> "$STATE"
  echo "[$TS] quota init: base_calls=$calls base_actual=$actual bal_est=$BASE (快照基准, 此后仅计新增)" >> "$QLOG"
  exit 0
fi

L_CALLS=$(sed -n 1p "$STATE"); L_ACTUAL=$(sed -n 2p "$STATE"); BAL=$(sed -n 3p "$STATE"); L_KNOWN=$(sed -n 4p "$STATE" 2>/dev/null || echo 0)
d_calls=$(( calls - L_CALLS )); [ "$d_calls" -lt 0 ] && d_calls=0
d_actual=$(( actual - L_ACTUAL )); [ "$d_actual" -lt 0 ] && d_actual=0
d_known=$(( known - L_KNOWN )); [ "$d_known" -lt 0 ] && d_known=0
d_unknown=$(( d_calls - d_known )); [ "$d_unknown" -lt 0 ] && d_unknown=0
inc=$(( d_actual + d_unknown * PER ))
BAL=$(( BAL - inc )); [ "$BAL" -lt 0 ] && BAL=0

echo "$calls" > "$STATE"; echo "$actual" >> "$STATE"; echo "$BAL" >> "$STATE"; echo "$known" >> "$STATE"
echo "[$TS] d_calls=$d_calls d_actual=$d_actual d_unknown=$d_unknown inc=$inc bal_est=$BAL" >> "$QLOG"

if [ "$BAL" -lt "$THRESHOLD" ]; then
  MSG="[额度告警] 方舟估算剩余 $BAL tokens（阈值 $THRESHOLD），快照基准 $BASE，新增估算消耗 $inc；请及时充值/续费（精确值以火山控制台为准）"
  echo "[$TS] ALERT $MSG" >> "$QLOG"
  bash /home/agent/work/tools/send-result-mail.sh "$MSG" "$QLOG" 2>/dev/null
fi
