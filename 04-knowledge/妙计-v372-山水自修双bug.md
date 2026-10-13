# 妙计：山水自主修复 v3.7 双 bug（空结果 + STALL 卡死）
> 签发：总工 → 执行：山水（worker 自主）｜优先级：高｜授权：总工本次**例外**授权修改自身 worker.py（v3.7.2 补丁）

你是山水 worker。总工授权你本次**例外**修改自己的 worker.py，修复两个已实锤的 bug。补丁由「发展」写好并实测通过（幂等 + 锚点校验 + 备份 + 编译闸），你只需原样打上并验证。**铁律：任何一步输出异常就立即停止、在 result 写明；绝不重启服务；绝不 git commit/push。**

## 背景（已取证，勿再调查）
- **bug1 空结果**：Doubao-Seed-Evolving 把整段回复塞进 `<seed:think_xxx>...</think_xxx>` 思考块，`strip_think_tags()` 剥光 → result 只剩完成头（19:56 / 20:13 两张自检卡实锤，均 `tokens=?`）。
- **bug2 STALL 卡死**：`spawn_auto_task()` 目标状态行不变就 `return None`；上游空结果 → AI 没更新 backlog 状态行 → sig 永不变 → 自主派发每 60s 跳过、永久冻结（今日已 64 次）。
- **根因关联**：bug1 是因，bug2 是果（没产出 → 没更新状态行 → STALL 永不放行）。

## 步骤 1／4：创建补丁脚本（内容由发展提供，原样落盘，勿改）
```bash
cat > /home/agent/work/patch_v372.py <<'PYEOF'
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""patch_v372.py — 山水 worker.py 双 bug 修复补丁（v3.7.2）
修复：① 任务 result 空结果（模型整段回复进 <seed:think_xxx> 思考块被剥光）
      ② 自主派发 STALL 永久卡死（同一目标状态行不变就 return None 不再推进）
用法: python3 patch_v372.py [worker.py路径]   # 默认 /home/agent/worker/worker.py
行为: 备份 -> 4 处锚点精确替换(幂等，已修复则跳过) -> 任一锚点 MISS 则中止不写回
      -> 写回后 py_compile 校验闸。**不重启服务**（重启按部署铁律单独做）。
安全: 只在全部锚点命中(或已修复)时才写回；编译失败则提示回滚命令。
"""
import sys
import shutil
import py_compile
from pathlib import Path

TARGET = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('/home/agent/worker/worker.py')
BACKUP = TARGET.parent / (TARGET.name + '.bak-pre-v372')

# ============ 4 处锚点（old = 线上原文，new = v3.7.2 修复版）============

OLD1 = '''def strip_think_tags(text: str) -> str:
    """剥离方舟 seed 系模型原样回传的思考块（<seed:think_xxx>...</think_xxx>）——
    思考内容不进执行提取与结果文件（2026-10-13 实测：端点把思考块混在 content 里，
    且思考块内的示例命令有被 extract_shell_blocks 误提取执行的风险）"""
    return re.sub(r'<seed:think_[^>]*>.*?</think_[^>]*>', '', text, flags=re.DOTALL).strip()'''

NEW1 = '''def strip_think_tags(text: str) -> str:
    """剥离方舟 seed 系模型原样回传的思考块（<seed:think_xxx>...</think_xxx>）——
    思考内容不进执行提取与结果文件（2026-10-13 实测：端点把思考块混在 content 里，
    且思考块内的示例命令有被 extract_shell_blocks 误提取执行的风险）。
    v3.7.2 空结果修复：若剥离后整体为空（模型把全部回复塞进思考块，2026-10-13 自检
    连续两张空 result 实锤），回退抽取思考块内正文——有空输出远胜于空 result。"""
    stripped = re.sub(r'<seed:think_[^>]*>.*?</think_[^>]*>', '', text, flags=re.DOTALL).strip()
    if stripped:
        return stripped
    inner = re.sub(r'<seed:think_[^>]*>', '', text, flags=re.DOTALL)
    inner = re.sub(r'</think_[^>]*>', '', inner, flags=re.DOTALL).strip()
    return inner'''

OLD2 = "AUTONOMY_DIR = BASE / 'logs' / 'autonomy'   # v3.6 自主模式配额计数目录"

NEW2 = ("AUTONOMY_DIR = BASE / 'logs' / 'autonomy'   # v3.6 自主模式配额计数目录\n"
        "STALL_RETRY_AFTER = 6                        # v3.7.2：同一目标连续 STALL 跳过 N 次后放行一次重试（自愈，防永久卡死；60s/次 ≈ 6min）")

OLD3 = '''    sig_file = AUTONOMY_DIR / 'last-spawn.sig'
    try:
        last_sig = sig_file.read_text(encoding='utf-8').strip() if sig_file.exists() else ''
    except OSError:
        last_sig = ''
    if last_sig == sig:
        log(f'AUTO STALL: 目标状态行未变化（AI 无心跳），跳过派发: {item[:60]}')
        return None
    if not autonomy_budget_left():
        return None'''

NEW3 = '''    sig_file = AUTONOMY_DIR / 'last-spawn.sig'
    stall_file = AUTONOMY_DIR / 'stall-count'
    try:
        last_sig = sig_file.read_text(encoding='utf-8').strip() if sig_file.exists() else ''
    except OSError:
        last_sig = ''
    if last_sig == sig:
        # STALL 守卫：目标状态行未变（AI 无心跳）→ 防死循环不狂派；
        # 但不永久冻结——连续跳过 STALL_RETRY_AFTER 次后放行一次重试（自愈），
        # 避免上游空结果 / AI 漏改状态行导致自主派发永久卡死（2026-10-13 验收实锤）。
        try:
            stalls = int(stall_file.read_text(encoding='utf-8').strip() or '0') if stall_file.exists() else 0
        except (OSError, ValueError):
            stalls = 0
        stalls += 1
        try:
            stall_file.write_text(str(stalls), encoding='utf-8')
        except OSError:
            pass
        if stalls < STALL_RETRY_AFTER:
            log(f'AUTO STALL: 目标状态行未变化（AI 无心跳），跳过派发 [{stalls}/{STALL_RETRY_AFTER}]: {item[:60]}')
            return None
        log(f'AUTO STALL 自愈：连续 {stalls} 次无心跳，放行一次重试: {item[:60]}')
        try:
            stall_file.write_text('0', encoding='utf-8')
        except OSError:
            pass
    else:
        # 状态行有变（有心跳/有推进）：重置 stall 计数
        try:
            stall_file.write_text('0', encoding='utf-8')
        except OSError:
            pass
    if not autonomy_budget_left():
        return None'''

OLD4 = '''    if draft:
        (DONE_DIR / f'{name}.draft.md').write_text(draft, encoding='utf-8')
    reply = final
    tokens = getattr(usage, 'total_tokens', None) if usage else None'''

NEW4 = '''    if draft:
        (DONE_DIR / f'{name}.draft.md').write_text(draft, encoding='utf-8')
    reply = final
    if not reply.strip():
        # v3.7.2 最终兜底：任何形态（整段思考块/纯空白/纯 tool_call 垃圾）剥离后为空，
        # 也绝不写空 result——占位 + 指明排查方向（2026-10-13 验收实锤空 result bug）
        log(f'TASK LLM EMPTY {name} 剥离后为空，写兜底占位')
        reply = ('【worker 兜底】模型回复经思考块/草稿区/tool_call 剥离后为空。\\n'
                 '可能形态：整段思考块 / 纯空白 / 纯 tool_call 垃圾。请复查端点输出，'
                 '原始回复长度见同任务上方 TASK LLM OK 日志行。')
    tokens = getattr(usage, 'total_tokens', None) if usage else None'''

PAIRS = [
    ('P1 strip_think_tags 空结果回退', OLD1, NEW1),
    ('P2 STALL_RETRY_AFTER 常量', OLD2, NEW2),
    ('P3 STALL 自愈重试', OLD3, NEW3),
    ('P4 process_task 空结果兜底占位', OLD4, NEW4),
]


def main():
    if not TARGET.exists():
        print(f'ABORT: 目标不存在 {TARGET}')
        sys.exit(2)
    text = TARGET.read_text(encoding='utf-8')

    if not BACKUP.exists():
        shutil.copy2(TARGET, BACKUP)
        print(f'BACKUP  -> {BACKUP}')
    else:
        print(f'BACKUP  已存在（不覆盖）-> {BACKUP}')

    miss = []
    for name, old, new in PAIRS:
        if new in text:
            print(f'  [already] {name}')
            continue
        if old not in text:
            miss.append(name)
            print(f'  [MISS]   {name}：原锚点未找到')
            continue
        if text.count(old) != 1:
            miss.append(name)
            print(f'  [MISS]   {name}：锚点出现 {text.count(old)} 次（应 1 次）')
            continue
        text = text.replace(old, new, 1)
        print(f'  [patched] {name}')

    if miss:
        print('ABORT: 以下锚点异常，未写回 live 文件：')
        for m in miss:
            print('   - ' + m)
        print('请人工核对 worker.py 是否已部分修复/已漂移；确认勿重启。')
        sys.exit(1)

    TARGET.write_text(text, encoding='utf-8')
    try:
        py_compile.compile(str(TARGET), doraise=True)
        print(f'PYCOMPILE OK -> {TARGET}')
    except py_compile.PyCompileError as e:
        print(f'PYCOMPILE FAIL: {e}')
        print(f'回滚命令: cp "{BACKUP}" "{TARGET}"')
        sys.exit(3)
    print('DONE: 补丁应用成功（未重启；请按部署铁律：先 systemctl restart ai-worker，后派发验证）')


if __name__ == '__main__':
    main()
PYEOF
echo "patcher written: $(wc -l < /home/agent/work/patch_v372.py) lines"
```

## 步骤 2／4：应用补丁（自动备份 + 4 处锚点替换 + 编译闸）
```bash
python3 /home/agent/work/patch_v372.py /home/agent/worker/worker.py
```
判定：
- 输出含 `DONE` 且 `PYCOMPILE OK` → 进步骤 3
- 输出含 `ABORT` / `MISS` / `PYCOMPILE FAIL` → **立即停止**：把完整输出写进 result，**不要重启**，结束任务

## 步骤 3／4：验证补丁行为（导入打过补丁的 worker 断言）
```bash
python3 - <<'PYEOF'
import importlib.util
s = importlib.util.spec_from_file_location('w', '/home/agent/worker/worker.py')
w = importlib.util.module_from_spec(s); s.loader.exec_module(w)
r = w.strip_think_tags('<seed:think_x>完整答案内容</think_x>')
assert '完整答案内容' in r, 'FAIL: 整段思考块未回退'
assert '思考' not in w.strip_think_tags('前<seed:think_x>思考</think_x>后'), 'FAIL: 混合块未剥'
assert w.STALL_RETRY_AFTER == 6, 'FAIL: STALL 常量缺失'
print('VERIFY OK: 空结果回退 + STALL 自愈常量均在')
PYEOF
```
断言失败 → **回滚**：`cp /home/agent/worker/worker.py.bak-pre-v372 /home/agent/worker/worker.py`，result 写明回滚原因，不重启，结束。

## 步骤 4／4：写结论（**不重启**）
result 必含：
- 补丁应用 + 本地验证：通过 / 失败（附完整输出）
- 备份位置：`/home/agent/worker/worker.py.bak-pre-v372`
- **未重启**（遵铁律⑤：重启 live 服务属重大变更，留总工确认）。补丁已写盘，将在下次重启生效——每日重生 ≤24h 自动加载，或总工下令重启 / 发展代劳。
- 复盘一句：bug1（空结果）是因，bug2（STALL 卡死）是果；修复后 result 不再空、自主派发有产出即会更新状态行自愈。

## 红线（违反即违纪）
1. **不重启 ai-worker**（重启 = 部署铁律「先 restart 后派发」，由发展 / 总工执行）
2. **不 git commit / push**（代码仓库对你只读；补丁落仓库由发展同步）
3. 编译不过 / 断言不过 → 立即回滚，绝不带病留盘
4. 本授权仅限这次 v3.7.2 双 bug 补丁，不代表今后可自改代码
