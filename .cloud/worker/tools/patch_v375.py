#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""patch_v375.py — worker.py v3.7.5 确定性侦察兜底
v3.7.4 已覆盖"有命令证据/有计划"两形态；但模型有时零产出（纯思考块/空白，无上下文）。
本补丁加 _auto_recon()：模型零产出时 worker 自己按任务关键词 grep 仓库/backlog/docs 取证，
把检索命中喂给二阶段合成 → 保证有根据的正文产出，不依赖模型肯不肯动手。
"""
import sys
import shutil
import py_compile
from pathlib import Path

TARGET = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('/home/agent/worker/worker.py')
BACKUP = TARGET.parent / (TARGET.name + '.bak-pre-v375')

OLD_FUNC_ANCHOR = "def process_task(client, task_path: Path):\n    name = task_path.name"

NEW_FUNC = '''def _auto_recon(content: str) -> str:
    """v3.7.5 确定性侦察：模型零产出时，worker 自己按任务关键词 grep 仓库/backlog/docs 取证。
    返回检索命中文本（截断 3000）；无命中 -> ''。不依赖模型是否肯调工具。"""
    kws: list = []
    for w in re.findall(r'[A-Za-z_][A-Za-z0-9_]{3,}', content):
        if w.lower() not in ('http', 'https', 'true', 'false', 'model', 'task') and w not in kws:
            kws.append(w)
    stop_cn = ('研究', '任务', '语义', '取证', '结论', '输出', '输入', '范围', '能否', '外部',
               '调度', '改写', '中文', '正文', '命令', '以下', '以上', '请直接', '模组', '验证',
               '置顶', '基于', '通过', '获得', '如下')
    for w in re.findall(r'[一-龥]{2,}', content):
        if w not in stop_cn and w not in kws:
            kws.append(w)
    kws = kws[:6]
    if not kws:
        return ''
    pat = '|'.join(re.escape(k) for k in kws)
    try:
        r = subprocess.run(['bash', '-c',
            f"grep -rIl -E '{pat}' /home/agent/Shanshui /home/agent/research-backlog.md /home/agent/work 2>/dev/null | head -8"],
            capture_output=True, text=True, timeout=60, cwd=str(WORK_DIR))
        files = ' '.join(r.stdout.split())
        if not files:
            return ''
        r2 = subprocess.run(['bash', '-c',
            f"grep -rIn -E '{pat}' {files} 2>/dev/null | head -20"],
            capture_output=True, text=True, timeout=60, cwd=str(WORK_DIR))
        return (r2.stdout or '').strip()[-3000:]
    except Exception:
        return ''


def process_task(client, task_path):
    name = task_path.name'''

OLD_ELSE = '''        else:
            # 真·无正文、无证据、无计划 → 兜底占位（绝不空白）
            log(f'TASK LLM EMPTY {name} 无正文无上下文，写兜底占位')
            reply = ('【worker 兜底】模型回复经思考块/草稿区/tool_call 剥离后为空，且无任何上下文。\\n'
                     '可能形态：纯空白。请复查端点输出。')'''

NEW_ELSE = '''        else:
            # v3.7.5 确定性侦察兜底：模型零产出时 worker 自己 grep 取证再合成（不依赖模型肯不肯动手）
            log(f'TASK RECON   {name} 模型零产出，worker 确定性侦察取证')
            recon = _auto_recon(content)
            if recon.strip():
                synth_task = (
                    f'原任务：\\n{content}\\n\\n已通过检索仓库/文档取证：\\n{recon}\\n\\n'
                    '请基于以上检索结果，用中文正文直接输出研究结论（≤300字，结论置顶）；严禁输出工具调用或思考块。'
                )
                try:
                    reply2, _u3 = chat_completions_stream(client, model, [
                        {'role': 'system', 'content': SYSTEM_PROMPT_EFFECTIVE},
                        {'role': 'user', 'content': synth_task},
                    ])
                    reply2 = strip_think_tags(redact(reply2))
                    _f3, _d3 = strip_draft(reply2)
                    reply2 = strip_tool_calls(_f3).strip()
                    if reply2:
                        reply = reply2 + '\\n\\n---\\n（据 worker 确定性侦察取证合成，检索命中见下）\\n' + recon
                        log(f'TASK RECON OK {name} 侦察合成正文 {len(reply2)} 字')
                    else:
                        reply = '（模型零产出，以下为 worker 侦察取证）\\n' + recon
                        log(f'TASK RECON SYNTH EMPTY {name}')
                except Exception as e:
                    log(f'TASK RECON ERR {name}: {type(e).__name__}: {e}')
                    reply = '（侦察合成异常，以下为 worker 侦察取证）\\n' + recon
            else:
                log(f'TASK LLM EMPTY {name} 模型零产出且侦察无果，写兜底占位')
                reply = ('【worker 兜底】模型回复剥离后为空，且确定性侦察无相关结果。\\n'
                         '请人工介入或换模型（见 MODEL-REGISTRY 一键换脑）。')'''


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
    # 1) 插入 _auto_recon
    if '_auto_recon' in text and 'def _auto_recon' in text:
        print('  [already] _auto_recon 已存在')
    elif OLD_FUNC_ANCHOR in text and text.count(OLD_FUNC_ANCHOR) == 1:
        text = text.replace(OLD_FUNC_ANCHOR, NEW_FUNC, 1)
        print('  [patched] 插入 _auto_recon 确定性侦察')
    else:
        miss.append('_auto_recon 锚点')

    # 2) 替换 else 分支为侦察兜底
    if 'TASK RECON' in text and '确定性侦察取证' in text and '侦察无果' in text:
        print('  [already] v3.7.5 侦察兜底')
    elif OLD_ELSE in text and text.count(OLD_ELSE) == 1:
        text = text.replace(OLD_ELSE, NEW_ELSE, 1)
        print('  [patched] v3.7.5 确定性侦察兜底')
    else:
        miss.append('else 分支锚点')

    if miss:
        print('ABORT: 锚点异常，未写回：', miss)
        sys.exit(1)

    TARGET.write_text(text, encoding='utf-8')
    try:
        py_compile.compile(str(TARGET), doraise=True)
        print(f'PYCOMPILE OK -> {TARGET}')
    except py_compile.PyCompileError as e:
        print(f'PYCOMPILE FAIL: {e}')
        print(f'回滚命令: cp "{BACKUP}" "{TARGET}"')
        sys.exit(3)
    print('DONE: v3.7.5 补丁应用成功（未重启；按部署铁律先 restart 后派发验证）')


if __name__ == '__main__':
    main()
