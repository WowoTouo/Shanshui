#!/usr/bin/env bash
# cleanup.sh — DLC-001 §2 存储治理（零 token：shell 的活，不经过模型）
# 用法：
#   cleanup.sh          dry-run：只出清单到 logs/cleanup-dryrun-<日期>.md，不删任何文件
#   cleanup.sh --apply  真删（须总工批准清单后执行；删除记录落 logs/cleanup-apply-<日期>.md）
# 安全：拒绝 root 运行；只清理白名单范围；保留清单内文件永不删
set -uo pipefail

APPLY=0
[ "${1:-}" = "--apply" ] && APPLY=1

if [ "$(id -u)" -eq 0 ]; then
    echo "REFUSE: 不以 root 运行（agent 身份足够，且防误伤）" >&2
    exit 1
fi

BASE="${AGENT_HOME:-/home/agent}"
ME="$(id -un)"
STAMP="$(date +%F)"
OUT="$BASE/logs/cleanup-dryrun-$STAMP.md"
APPLY_LOG="$BASE/logs/cleanup-apply-$STAMP.md"
mkdir -p "$BASE/logs"

# 保留清单（find -regex 为全路径匹配，.* 前缀；命中即保留）
KEEP='.*(\.env|\.md|/learnings/|/tools/|/tasks/|/done/|/memory/|/proposals/|/dlc/|/\.git/)'

section() { printf '\n## %s\n' "$1"; }
count() { grep -c . <<<"$1" 2>/dev/null || echo 0; }

{
    printf '# 清理清单 %s\n' "$STAMP"
    printf '模式：%s\n' "$([ "$APPLY" -eq 1 ] && echo 'APPLY（真删）' || echo 'DRY-RUN（仅清单，未删）')"
    printf '执行者：%s · BASE=%s\n' "$ME" "$BASE"

    section '/tmp >24h（仅本人文件，排除 systemd 私有目录）'
    find /tmp -mindepth 1 -maxdepth 2 -user "$ME" -mmin +1440 \
        ! -path '/tmp/systemd-*' -printf '%TY-%Tm-%Td %TH:%TM %p\n' 2>/dev/null | head -100

    section 'work/ >7d 非保留中间产物'
    if [ -d "$BASE/work" ]; then
        find "$BASE/work" -mindepth 1 -type f -mtime +7 ! -regex "$KEEP" \
            -printf '%TY-%Tm-%Td %p\n' 2>/dev/null | head -200
    else
        echo '(work/ 不存在)'
    fi

    section 'logs/ >14d（非 .md；.md 为日报/清单类记忆，保留）'
    find "$BASE/logs" -mindepth 1 -type f -mtime +14 ! -name '*.md' \
        -printf '%TY-%Tm-%Td %p\n' 2>/dev/null | head -100

    section '__pycache__（仅 work/ 下 >7d）'
    if [ -d "$BASE/work" ]; then
        find "$BASE/work" -type d -name __pycache__ -mtime +7 2>/dev/null | head -50
    fi

    section 'pip 缓存（~/.cache/pip，仅报告大小；apply 且 >30d 未用才清）'
    if [ -d "$HOME/.cache/pip" ]; then
        du -sh "$HOME/.cache/pip" 2>/dev/null
        echo "mtime: $(stat -c %y "$HOME/.cache/pip" 2>/dev/null | cut -d. -f1)"
    else
        echo '(无 pip 缓存)'
    fi

    section 'gradle/npm 缓存（仅报告，永不自动删——重下浪费 3Mbps 带宽）'
    for d in "$HOME/.gradle" "$HOME/.npm"; do
        [ -d "$d" ] && du -sh "$d" 2>/dev/null || true
    done
    echo '(以上仅列示，apply 模式也不删)'

    section '磁盘现状'
    df -h / | tail -1

    printf '\n---\n保留清单：.env、*.md、learnings/、tools/、tasks/、done/、memory/、proposals/、dlc/、.git/\n'
    printf '系统路径/凭据/他人文件不在清理范围。\n'
} > "$OUT"

echo "清单已写入 $OUT"

if [ "$APPLY" -eq 0 ]; then
    echo "dry-run 模式，未删任何文件。批准后执行：bash $0 --apply"
    exit 0
fi

# ===== APPLY：按上述同条件真删（保留清单硬编码同上）=====
{
    printf '# 清理执行记录 %s（APPLY）\n' "$STAMP"
    printf '操作者：%s\n\n' "$ME"

    printf '## /tmp >24h\n'
    find /tmp -mindepth 1 -maxdepth 2 -user "$ME" -mmin +1440 \
        ! -path '/tmp/systemd-*' -delete 2>/dev/null
    echo 'done'

    printf '## work/ >7d 非保留\n'
    if [ -d "$BASE/work" ]; then
        find "$BASE/work" -mindepth 1 -type f -mtime +7 ! -regex "$KEEP" -delete 2>/dev/null
    fi
    echo 'done'

    printf '## logs/ >14d 非 .md → gzip；.gz >30d → 删\n'
    find "$BASE/logs" -mindepth 1 -type f -mtime +14 ! -name '*.md' ! -name '*.gz' \
        -exec gzip -9 {} \+ 2>/dev/null
    find "$BASE/logs" -mindepth 1 -type f -name '*.gz' -mtime +30 -delete 2>/dev/null
    echo 'done'

    printf '## work/ __pycache__ >7d\n'
    if [ -d "$BASE/work" ]; then
        find "$BASE/work" -type d -name __pycache__ -mtime +7 -exec rm -rf {} \+ 2>/dev/null
    fi
    echo 'done'

    printf '## pip 缓存（>30d 未用才清）\n'
    if [ -d "$HOME/.cache/pip" ]; then
        if [ -n "$(find "$HOME/.cache/pip" -mmin -43200 2>/dev/null | head -1)" ]; then
            echo 'pip 缓存 30 天内被用过，跳过'
        else
            rm -rf "$HOME/.cache/pip"
            echo 'pip 缓存已清'
        fi
    fi

    printf '\n磁盘现状：\n'
    df -h / | tail -1
} > "$APPLY_LOG"

echo "APPLY 完成，执行记录：$APPLY_LOG"
