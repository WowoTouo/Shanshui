#!/bin/bash
# 山水研究成果自动上云（服务器 -> Gitee）
# 把 done/ 任务结果 + work/playbooks + work/learnings 增量镜像进仓库 research/，commit + push gitee
# 多写入方安全：先 fetch+rebase gitee 上游再提交，避免与本地/科学的提交 non-ff 冲突
# 零 token、纯文件操作；crontab 每 2 小时触发
set -uo pipefail
REPO=/home/agent/Shanshui
LOG=/home/agent/logs/sync-research.log
cd "$REPO" || exit 1
git fetch gitee main 2>>"$LOG"
if ! git rebase gitee/main >>"$LOG" 2>&1; then
  git rebase --abort 2>/dev/null
  echo "$(date '+%F %T') sync-research: rebase 冲突，跳过本轮" >> "$LOG"
  exit 0
fi
mkdir -p research/results research/playbooks research/learnings
for f in /home/agent/done/*.result.md; do [ -f "$f" ] && cp -u "$f" research/results/ 2>/dev/null; done
for f in /home/agent/work/playbooks/*;  do [ -f "$f" ] && cp -u "$f" research/playbooks/ 2>/dev/null; done
for f in /home/agent/work/learnings/*;  do [ -f "$f" ] && cp -u "$f" research/learnings/ 2>/dev/null; done
git add research/ 2>/dev/null
if git diff --cached --quiet; then
  echo "$(date '+%F %T') sync-research: no change" >> "$LOG"
else
  git commit -q -m "research: auto-sync $(date +%Y-%m-%d_%H:%M)"
  timeout 60 git push gitee main 2>&1 | tail -1 >> "$LOG"
  echo "$(date '+%F %T') sync-research: pushed" >> "$LOG"
fi
