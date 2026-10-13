#!/bin/bash
# gitpush.sh — GitHub push 健壮重试（应对 E6 间歇性 reset / Could not connect）
# 用法: ./gitpush.sh [remote] [branch]   默认 origin main
# 修正点: 直接判 git 退出码(不接 tail 误判); 仅网络类错误重试, 认证/拒绝类立即停
set -u
REMOTE="${1:-origin}"
BRANCH="${2:-main}"
MAX=15
DELAY=4
for i in $(seq 1 "$MAX"); do
  echo "[push] try $i/$MAX -> $REMOTE/$BRANCH"
  out=$(git push "$REMOTE" "$BRANCH" 2>&1); rc=$?
  echo "$out"
  if [ "$rc" -eq 0 ]; then echo "[push] OK"; exit 0; fi
  # 非网络错误(凭证/拒绝/权限)不重试, 立即停
  if echo "$out" | grep -qiE "denied|reject|not authorized|Permission|invalid|fatal: unable to access.*404|already exists"; then
    echo "[push] 非网络错误, 停止重试"; exit 1
  fi
  echo "[push] 网络错误, sleep ${DELAY}s 后重试"
  sleep "$DELAY"
  DELAY=$(( DELAY*2 > 90 ? 90 : DELAY*2 ))   # 指数退避, 上限 90s
done
echo "[push] ABORT after $MAX tries"
exit 1
