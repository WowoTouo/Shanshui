#!/bin/bash
# 山水工程 · Gradle 构建兼容性验证脚本
# 用法: verify-build.sh <JAVA_HOME路径> <tag>
# 例:   verify-build.sh /usr/lib/jvm/zulu27 27
# 输出: /home/agent/logs/build-<tag>.log（全程留痕）+ stdout 尾部摘要
set -u
JH="$1"
TAG="$2"
export JAVA_HOME="$JH"
export PATH="$JH/bin:$PATH"
cd /home/agent/Shanshui || { echo "NO_REPO: /home/agent/Shanshui 不存在"; exit 1; }
LOG="/home/agent/logs/build-${TAG}.log"
{
    echo "=== $(date '+%F %T') build test: JAVA_HOME=$JH ==="
    java -version 2>&1
    echo "--- gradle build --no-daemon ---"
    gradle build --no-daemon --console=plain 2>&1
    echo "GRADLE_EXIT=$?"
} > "$LOG" 2>&1
echo "===== $LOG 尾部摘要 ====="
tail -30 "$LOG"
