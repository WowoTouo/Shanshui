#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""patch_v37.py — worker.py v3.6.1 收尾 + v3.7 DLC 体系补丁（2026-10-13）
补丁内容（9 处锚点替换，ast.parse 自检，幂等可重跑）：
  1. 常量块：PROMPT_FILE / DLC_DIR / CLEANUP_DIR / PROPOSALS_DIR / MAIL_SCRIPT / WORKER_VERSION
  2. 模块 docstring：补 v3.6.1 / v3.7 说明
  3. extract_tool_calls + strip_tool_calls（v3.6.1：方舟 seed:tool_call XML 兜底解析）
  4. load_guides / build_system_prompt → v3.7 四层注入（PROMPT→ONBOARDING→AUTONOMY→dlc/*.md）
  5. spawn_auto_task → v3.6.1 重写（_current_auto_target 三元组 + STALL 进度守卫 + 秒级时间戳）
  6. maybe_run_cleanup + check_proposals（v3.7 零 token 治理）
  7. main()：四层加载日志 + 启动补检提案
  8. 空闲分支：清理检查 + 提案检测接线
  9. 启动日志带版本号
用法: python patch_v37.py [worker.py 路径]
"""
import ast
import sys
from pathlib import Path
SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).with_name('worker.py')
src = SRC.read_text(encoding='utf-8')
changed = 0
def sub(old: str, new: str, tag: str, marker: str):
    """锚点替换：marker 已在源码中 → 跳过（幂等）；锚点缺失/不唯一 → 中止。"""
    global src, changed
    if marker in src:
        print(f'SKIP (already patched): {tag}')
        return
    n = src.count(old)
    if n != 1:
        raise SystemExit(f'ANCHOR MISS/AMBIGUOUS ({n}x): {tag}\n--- 锚点前 80 字符 ---\n{old[:80]!r}')
    src = src.replace(old, new, 1)
    changed += 1
    print(f'OK ({changed}/9): {tag}')
# ===== 前置自检：v3.6.1 工作树编辑必须已在（process_task 提命令 + next_plan_item 三元组）=====
for must in (
    'tool_cmds = extract_tool_calls(final)',
    r"m = re.match(r'^\s*-\s*\[( |~)\]\s*(.+)$', line)",
    'return plan.parent.name, m.group(2).strip(), line.strip()',
):
    if must not in src:
        raise SystemExit(f'PRECHECK FAIL: v3.6.1 工作树编辑缺失 -> {must[:60]}')
print('PRECHECK: v3.6.1 工作树编辑在位（process_task 提命令 / next_plan_item 三元组）')
# ============ 1/9 常量块 ============
OLD1 = "AUTONOMY_DIR = BASE / 'logs' / 'autonomy'   # v3.6 自主模式配额计数目录\n"
NEW1 = OLD1 + (
    "PROMPT_FILE = BASE / 'PROMPT.md'            # v3.7 自主核心提示词（四层注入第 1 层）\n"
    "DLC_DIR = BASE / 'dlc'                      # v3.7 DLC 扩展层目录（dlc/*.md 按文件名排序挂载）\n"
    "CLEANUP_DIR = BASE / 'logs' / 'cleanup'     # v3.7 清理循环每日 marker 目录\n"
    "PROPOSALS_DIR = BASE / 'proposals'          # v3.7 权限提案目录（DLC-001 §3，默认拒绝）\n"
    "MAIL_SCRIPT = BASE / 'work' / 'tools' / 'send-result-mail.sh'  # v3.7 提案邮件通知（msmtp 通道）\n"
    "WORKER_VERSION = 'v3.7'                     # 版本号（启动日志可见）\n"
)
sub(OLD1, NEW1, '1/9 常量块', 'WORKER_VERSION')
