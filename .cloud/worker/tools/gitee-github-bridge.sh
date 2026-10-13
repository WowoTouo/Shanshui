#!/bin/bash
# 双 remote 镜像泵：Gitee <-> GitHub 自动对齐（服务器 7x24 在线，本地关机也能同步）
# 用法：sudo -H -u agent bash /home/agent/work/tools/gitee-github-bridge.sh
# 逻辑：fetch gitee -> fast-forward merge -> push gitee -> push origin(GitHub, 重试3次碰窗口)
LOG=/home/agent/logs/bridge.log
R=/home/agent/Shanshui
TS=$(date '+%Y-%m-%d %H:%M:%S')
echo "[$TS] bridge start" >> $LOG

cd "$R" || { echo "[$TS] cd fail" >> $LOG; exit 1; }

git fetch gitee main >> $LOG 2>&1
if git merge --ff-only gitee/main >> $LOG 2>&1; then
    echo "[$TS] ff-merge gitee OK" >> $LOG
else
    echo "[$TS] ff-merge skip (already up or conflict)" >> $LOG
fi

git push gitee main >> $LOG 2>&1 && echo "[$TS] push gitee OK" >> $LOG

for i in 1 2 3 4 5; do
    if git push origin main >> $LOG 2>&1; then
        echo "[$TS] push github OK (try $i)" >> $LOG
        break
    fi
    echo "[$TS] push github try $i fail, retry..." >> $LOG
    sleep 15
done

echo "[$TS] bridge done" >> $LOG
