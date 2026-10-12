#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
山水工程 防火墙 SSH 白名单自动同步 + 过期清理
================================================
场景：用户有两条上网通道——宽带 + 移动 WiFi（晚上宽带重启会切移动 WiFi），
两边公网 IPv4 / IPv6 前缀都会动态变化。本脚本由 Windows 计划任务每 15 分钟执行：
  1. 检测当前出口 IPv4（多源轮试）与 IPv6 /64 前缀
  2. 不在防火墙 22 白名单 → tccli CreateFirewallRules 增量追加（只增）
  3. 清理过期规则：描述以 'SSH auto' 开头且日期起 >=14 天未活跃的自动规则，
     手动规则永不碰、当前活跃出口永不删、单轮最多删 3 条（防误删）
"""
import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

INSTANCE_ID = 'lhins-lez7aalf'
TCCLI = r'C:\Users\CHN_W\.workbuddy\binaries\python\envs\default\Scripts\tccli.exe'
# 2026-10-13 起日志改 md 格式（用户指令：生成的报告日志尽可能用 md）；
# 此前的纯文本记录留存于同目录 fw-sync.log，无任何脚本消费本日志
LOG = Path(r'D:\窝窝头的1.20.2整合包\Shanshui\.cloud\worker\logs\fw-sync.md')
STALE_DAYS = 14
MAX_DELETE_PER_RUN = 3
# Windows 无窗口运行（2026-10-13 用户要求：后台安静跑，不弹控制台窗口）：
# 计划任务已切 pythonw.exe（本身无控制台），子进程再加 CREATE_NO_WINDOW 双保险
CREATE_NO_WINDOW = 0x08000000


def log(msg: str):
    LOG.parent.mkdir(parents=True, exist_ok=True)
    if not LOG.exists():
        with open(LOG, 'w', encoding='utf-8') as f:
            f.write('# 山水工程 防火墙白名单同步日志\n\n'
                    '> 2026-10-13 起改为 md 格式；此前纯文本记录见同目录 `fw-sync.log`\n\n')
    with open(LOG, 'a', encoding='utf-8') as f:
        f.write(f'- `{datetime.now():%Y-%m-%d %H:%M:%S}` {msg}\n')


def tccli(*args) -> str:
    # 文件重定向而非管道捕获：Windows 计划任务环境下 subprocess 管道
    # 捕获 tccli 输出会得到 None（Task Scheduler 句柄怪癖，2026-10-13 实测）
    # tmp 文件只覆盖不删除：助手工具会话的 safe-delete 会拦 unlink
    tmp = LOG.parent / 'tccli-out.tmp'
    with open(tmp, 'w', encoding='utf-8', errors='replace') as fo:
        subprocess.run([TCCLI, *args], stdout=fo, stderr=subprocess.STDOUT,
                       timeout=60, creationflags=CREATE_NO_WINDOW)
    return tmp.read_text(encoding='utf-8', errors='replace')


def curl_silent(*args) -> str:
    """静默 curl：文件重定向 + 无窗口（与 tccli 同款免疫，防计划任务句柄怪癖）"""
    tmp = LOG.parent / 'curl-out.tmp'
    with open(tmp, 'w', encoding='utf-8', errors='replace') as fo:
        subprocess.run(['curl.exe', *args], stdout=fo, stderr=subprocess.DEVNULL,
                       timeout=10, creationflags=CREATE_NO_WINDOW)
    return tmp.read_text(encoding='utf-8', errors='replace')


def is_public_v4(ip: str) -> bool:
    if ip.startswith(('10.', '127.', '192.168.', '169.254.', '0.')):
        return False
    if re.match(r'^172\.(1[6-9]|2\d|3[01])\.', ip):
        return False
    return bool(re.match(r'^\d{1,3}(\.\d{1,3}){3}$', ip))


def get_public_v4():
    for url in ('https://cip.cc', 'https://myip.ipip.net', 'http://members.3322.org/dyndns/getip'):
        try:
            out = curl_silent('-s', '--max-time', '6', url)
            m = re.search(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', out)
            if m and is_public_v4(m.group(1)):
                return m.group(1)
        except Exception:
            pass
    return None


def get_v6_prefix():
    try:
        out = curl_silent('-s', '-6', '--max-time', '6', 'https://api6.ipify.org').strip()
        m = re.match(r'^([0-9a-fA-F]{1,4}:[0-9a-fA-F]{1,4}:[0-9a-fA-F]{1,4}:[0-9a-fA-F]{1,4})', out)
        return m.group(1).lower() if m else None
    except Exception:
        return None


def main():
    v4 = get_public_v4()
    v6 = get_v6_prefix()
    if not v4 and not v6:
        log('WARN 取不到出口 IP（网络异常），本轮跳过')
        return

    raw = tccli('lighthouse', 'DescribeFirewallRules', '--InstanceId', INSTANCE_ID)
    try:
        rules = json.loads(raw)['FirewallRuleSet']
    except Exception as e:
        log(f'ERROR 解析防火墙规则失败: {e} | raw={raw[:200]}')
        return

    has_v4 = any(r['Port'] == '22' and v4 and r['CidrBlock'] == f'{v4}/32' for r in rules)
    has_v6 = any(r['Port'] == '22' and v6 and r['Ipv6CidrBlock'] == f'{v6}::/64' for r in rules)
    log(f'出口 v4={v4} v6={v6} | 白名单已有 v4={has_v4} v6={has_v6}')

    # --- 追加（只增不删的增量通道）---
    add = []
    stamp = datetime.now().strftime('%Y-%m-%d %H:%M')
    if v4 and not has_v4:
        add.append({'Protocol': 'TCP', 'Port': '22', 'CidrBlock': f'{v4}/32',
                    'Action': 'ACCEPT', 'FirewallRuleDescription': f'SSH auto {stamp}'})
    if v6 and not has_v6:
        add.append({'Protocol': 'TCP', 'Port': '22', 'Ipv6CidrBlock': f'{v6}::/64',
                    'Action': 'ACCEPT', 'FirewallRuleDescription': f'SSH auto v6 {stamp}'})
    if add:
        out = tccli('lighthouse', 'CreateFirewallRules', '--InstanceId', INSTANCE_ID,
                    '--FirewallRules', json.dumps(add, ensure_ascii=False))
        log(f'追加 {len(add)} 条 => {out.strip()[:200]}')
    else:
        log('无需变动')

    # --- 清理过期 auto 规则（2026-10-13 总工盯防②：白名单膨胀）---
    now = datetime.now()
    stale = []
    for r in rules:
        if r['Port'] != '22':
            continue
        desc = r.get('FirewallRuleDescription') or ''
        if not desc.startswith('SSH auto'):      # 手动规则永不碰
            continue
        if v4 and r['CidrBlock'] == f'{v4}/32':  # 当前活跃永不删
            continue
        if v6 and r['Ipv6CidrBlock'] == f'{v6}::/64':
            continue
        m = re.search(r'(\d{4}-\d{2}-\d{2})', desc)
        if not m:
            continue
        try:
            d = datetime.strptime(m.group(1), '%Y-%m-%d')
        except ValueError:
            continue
        if (now - d).days >= STALE_DAYS:
            stale.append(r)
    if stale:
        to_del = stale[:MAX_DELETE_PER_RUN]
        # 只传删除定位必需的最小字段集（AppType 等只读字段会让 tccli 拒收）
        minimal = []
        for r in to_del:
            item = {'Protocol': r['Protocol'], 'Port': r['Port'], 'Action': r.get('Action', 'ACCEPT')}
            if r.get('CidrBlock'):
                item['CidrBlock'] = r['CidrBlock']
            if r.get('Ipv6CidrBlock'):
                item['Ipv6CidrBlock'] = r['Ipv6CidrBlock']
            minimal.append(item)
        out = tccli('lighthouse', 'DeleteFirewallRules', '--InstanceId', INSTANCE_ID,
                    '--FirewallRules', json.dumps(minimal, ensure_ascii=False))
        log(f'清理 {len(to_del)}/{len(stale)} 条过期规则 => {out.strip()[:200]}')
    else:
        log('无过期规则')


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        log(f'FATAL {type(e).__name__}: {e}')
        sys.exit(1)
