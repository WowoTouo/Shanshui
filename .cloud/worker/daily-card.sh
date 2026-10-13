#!/usr/bin/env bash
# daily-card.sh — DLC-001 §1：每日 08:00 生成总结任务卡（cron 触发，零 token）
# 幂等：当天已生成则不重复；卡片进 tasks/ 由 worker 自动领取（无状态可续）
set -euo pipefail
BASE="${AGENT_HOME:-/home/agent}"
D="$(date +%F)"
Y="$(date -d 'yesterday' +%F)"
CARD="$BASE/tasks/auto-daily-$D.md"
[ -e "$CARD" ] && exit 0
mkdir -p "$BASE/tasks" "$BASE/memory/daily"
sed -e "s/__D__/$D/g" -e "s/__Y__/$Y/g" > "$CARD" <<'EOF'
# 任务：每日总结（DLC-001 §1 · 五元素日报）
覆盖窗口：__Y__ 08:00 → __D__ 08:00（过去 24 小时）

## 步骤
1. 采集（shell 先行，零 token）：
   - ls done/ | grep -E '__Y__|__D__'（昨日至今完成了哪些任务）
   - grep -E 'AUTO|ERROR|STALL|PROPOSAL|CLEANUP|GUIDES|TASK DONE' logs/worker.log | tail -60
   - cat logs/daily/__Y__.md 2>/dev/null || true（6 点 shell 摘要，若存在）
2. 写 memory/daily/__D__.md（目录不存在先建），五元素、总长 ≤200 字，缺数据写"无"：
   # 日报 __D__
   简述: <在做什么项目/任务，一句话>
   修复: <修了什么 bug，怎么修的>
   解决: <解决了什么难题，解法卡编号>
   推进: <进度到哪，下一步>
   沉淀: <新增 DLC/知识条目/解法卡，无则写"无">
3. 追加长期记忆锚点一行到 memory/MEMORY.md（不存在则创建，首行写 '# 山水工程服务器 AI 长期记忆'）：
   - __D__ <一句话摘要>
4. 经验评估：过去 24h 有没有值得固化的经验？
   - 有 → 按 DLC-001 §4 写 dlc/DLC-00N-<主题>.md（N=现有最大编号+1）或 work/learnings/<主题>.md，并在日报"沉淀"栏登记
   - 没有 → 跳过，不硬造

## 纪律
- 单轮完成，全程一次模型调用，不美化措辞（DLC-001 §1 开销控制）
- 命令一律写在 ```bash 块中（v3.6.1 纪律）；文件必须落盘，结论写进 result
EOF
echo "daily card -> $CARD"
