#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
山水工程 每周自动快照（Windows 计划任务每周一 09:00 执行）
================================================
Lighthouse 无自动快照策略 API，只能本地定时调 API 实现。
基线快照 lhsnap-1342c0fd（shanshui-baseline-20261013）永久保留不删；
自动快照按周命名 shanshui-auto-YYYYMMDD，保留最近 8 个（约两个月），更早自动清理。
"""
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

INSTANCE_ID = 'lhins-lez7aalf'
TCCLI = r'C:\Users\CHN_W\.workbuddy\binaries\python\envs\default\Scripts\tccli.exe'
# 2026-10-13 起日志改 md 格式（用户指令：生成的报告日志尽可能用 md）；
# 此前纯文本记录留存于同目录 weekly-snapshot.log，无任何脚本消费本日志
LOG = Path(r'D:\窝窝头的1.20.2整合包\Shanshui\.cloud\worker\logs\weekly-snapshot.md')
KEEP = 8
# Windows 无窗口运行（2026-10-13 用户要求：后台安静跑，不弹控制台窗口）：
# 计划任务已切 pythonw.exe（本身无控制台），子进程再加 CREATE_NO_WINDOW 双保险
CREATE_NO_WINDOW = 0x08000000


def log(msg: str):
    LOG.parent.mkdir(parents=True, exist_ok=True)
    if not LOG.exists():
        with open(LOG, 'w', encoding='utf-8') as f:
            f.write('# 山水工程 每周快照日志\n\n'
                    '> 2026-10-13 起改为 md 格式；此前纯文本记录见同目录 `weekly-snapshot.log`\n\n')
    with open(LOG, 'a', encoding='utf-8') as f:
        f.write(f'- `{datetime.now():%Y-%m-%d %H:%M:%S}` {msg}\n')


def tccli(*args) -> str:
    # 文件重定向而非管道捕获：Windows 计划任务环境下 subprocess 管道
    # 捕获 tccli 输出会得到 None（Task Scheduler 句柄怪癖，2026-10-13 实测）
    # tmp 文件只覆盖不删除：助手工具会话的 safe-delete 会拦 unlink
    tmp = LOG.parent / 'tccli-out.tmp'
    with open(tmp, 'w', encoding='utf-8', errors='replace') as fo:
        subprocess.run([TCCLI, *args], stdout=fo, stderr=subprocess.STDOUT,
                       timeout=120, creationflags=CREATE_NO_WINDOW)
    return tmp.read_text(encoding='utf-8', errors='replace')


def main():
    name = f'shanshui-auto-{datetime.now():%Y%m%d}'
    out = tccli('lighthouse', 'CreateInstanceSnapshot', '--InstanceId', INSTANCE_ID, '--SnapshotName', name)
    log(f'CreateInstanceSnapshot {name} => {out.strip()[:200]}')

    raw = tccli('lighthouse', 'DescribeSnapshots')
    try:
        snaps = json.loads(raw)['SnapshotSet']
    except Exception as e:
        log(f'ERROR 解析快照列表失败: {e} | raw={raw[:200]}')
        return

    auto = sorted(
        [s for s in snaps if (s.get('SnapshotName') or '').startswith('shanshui-auto-')],
        key=lambda s: s.get('CreateTime', ''), reverse=True,
    )
    if len(auto) > KEEP:
        old = auto[KEEP:]
        ids = [s['SnapshotId'] for s in old]
        out = tccli('lighthouse', 'DeleteSnapshots', '--SnapshotIds', json.dumps(ids))
        log(f'清理 {len(ids)} 个旧快照 {ids} => {out.strip()[:200]}')
    else:
        log(f'自动快照 {len(auto)} 个，未超 {KEEP} 保留上限，无需清理')


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        log(f'FATAL {type(e).__name__}: {e}')
        sys.exit(1)
