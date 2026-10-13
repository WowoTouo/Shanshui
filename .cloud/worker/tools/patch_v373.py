#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""patch_v373.py — 山水 worker.py v3.7.3 智能两阶段研究模式
修复：Doubao-Seed-Evolving 在长 prompt(15k)+复杂任务下整段工具调用/思考块（零正文）。
解法：一阶段任其跑命令取证 → 二阶段据执行证据合成正文结论（任务单一化 → 模型稳定）。
用法: python3 patch_v373.py [worker.py路径]   # 默认 /home/agent/worker/worker.py
行为: 备份 -> 锚点替换(幂等) -> MISS 中止不写回 -> py_compile 闸。不重启。
"""
import sys
import shutil
import py_compile
from pathlib import Path

TARGET = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('/home/agent/worker/worker.py')
BACKUP = TARGET.parent / (TARGET.name + '.bak-pre-v373')

OLD = '''    reply = final
    if not reply.strip():
        # v3.7.2 最终兜底：任何形态（整段思考块/纯空白/纯 tool_call 垃圾）剥离后为空，
        # 也绝不写空 result——占位 + 指明排查方向（2026-10-13 验收实锤空 result bug）
        log(f'TASK LLM EMPTY {name} 剥离后为空，写兜底占位')
        reply = ('【worker 兜底】模型回复经思考块/草稿区/tool_call 剥离后为空。\\n'
                 '可能形态：整段思考块 / 纯空白 / 纯 tool_call 垃圾。请复查端点输出，'
                 '原始回复长度见同任务上方 TASK LLM OK 日志行。')
    tokens = getattr(usage, 'total_tokens', None) if usage else None
    log(f'TASK LLM OK  {name} | model={model} tokens={tokens if tokens else "?"} reply_len={len(reply)}')

    # ===== 执行权 v2：提取并执行 shell 块（```bash 块 + tool_call 语法兜底）=====
    blocks = extract_shell_blocks(reply) + tool_cmds
    exec_log = ''
    if blocks:
        log(f'TASK EXEC   {name} 提取到 {len(blocks)} 个命令块')
        parts = ['\\n\\n---\\n## 执行记录（worker 自动执行）\\n']
        for i, cmd in enumerate(blocks, 1):
            ok, out = execute_shell(cmd)
            parts.append(f'### 命令 {i}\\n```bash\\n{cmd[:500]}\\n```\\n**{"成功" if ok else "失败/拒绝"}**\\n```\\n{out}\\n```\\n')
            log(f'TASK EXEC   {name} cmd#{i} ok={ok}')
        exec_log = '\\n'.join(parts)

    DONE_DIR.mkdir(exist_ok=True)
    result_path = DONE_DIR / f'{name}.result.md'
    result_path.write_text(
        redact(
            f'<!-- 任务 {name} 完成于 {datetime.now():%Y-%m-%d %H:%M:%S} -->\\n\\n{reply}\\n{exec_log}\\n'
        ),
        encoding='utf-8',
    )
    shutil.move(str(task_path), str(DONE_DIR / name))
    log(f'TASK DONE    {name} -> done/{name}.result.md')'''

NEW = '''    reply = final   # 一阶段正文：模型直接写结论则非空；整段工具调用则为空
    tokens = getattr(usage, 'total_tokens', None) if usage else None
    log(f'TASK LLM OK  {name} | model={model} tokens={tokens if tokens else "?"} phase1_len={len(reply)}')

    # ===== 执行权 v2：提取并执行 shell 块（```bash 块 + tool_call 语法兜底）=====
    blocks = extract_shell_blocks(reply) + tool_cmds
    exec_log = ''
    if blocks:
        log(f'TASK EXEC   {name} 提取到 {len(blocks)} 个命令块')
        parts = ['\\n\\n---\\n## 执行记录（worker 自动执行）\\n']
        for i, cmd in enumerate(blocks, 1):
            ok, out = execute_shell(cmd)
            parts.append(f'### 命令 {i}\\n```bash\\n{cmd[:500]}\\n```\\n**{"成功" if ok else "失败/拒绝"}**\\n```\\n{out}\\n```\\n')
            log(f'TASK EXEC   {name} cmd#{i} ok={ok}')
        exec_log = '\\n'.join(parts)

    # ===== v3.7.3 智能两阶段研究模式（避免长 prompt + 复杂任务触发模型退化）=====
    # 实证：模型面对"自己研究"的复杂任务会整段工具调用（零正文）；但把证据喂给它
    # "写结论"就稳定返回正文。故一阶段任其跑命令取证，二阶段据证据合成正文结论——
    # 每阶段任务单一 → 模型稳定，且产出必有正文结论。
    if not reply.strip():
        if exec_log.strip():
            log(f'TASK SYNTH   {name} 一阶段零正文，据执行证据二阶段合成结论')
            synth_task = (
                f'原任务：\\n{content}\\n\\n'
                f'已通过命令取证，执行结果如下：\\n{exec_log}\\n\\n'
                '请基于以上证据，用中文正文直接输出研究结论（≤300字，结论置顶）；'
                '严禁输出工具调用或思考块，只写结论正文。'
            )
            try:
                reply2, _u2 = chat_completions_stream(client, model, [
                    {'role': 'system', 'content': SYSTEM_PROMPT_EFFECTIVE},
                    {'role': 'user', 'content': synth_task},
                ])
                reply2 = strip_think_tags(redact(reply2))
                _f2, _d2 = strip_draft(reply2)
                reply2 = strip_tool_calls(_f2).strip()
                if reply2:
                    reply = reply2
                    log(f'TASK SYNTH OK {name} 合成正文 {len(reply)} 字')
                else:
                    reply = '（模型以工具调用取证，二阶段合成仍空，以下为命令执行证据）\\n' + exec_log
                    log(f'TASK SYNTH EMPTY {name} 二阶段仍空，回退执行证据')
            except Exception as e:
                log(f'TASK SYNTH ERR {name}: {type(e).__name__}: {e}')
                reply = '（二阶段合成异常，以下为命令执行证据）\\n' + exec_log
        else:
            # 无正文、无证据 → 兜底占位（绝不空白）
            log(f'TASK LLM EMPTY {name} 无正文无证据，写兜底占位')
            reply = ('【worker 兜底】模型回复经思考块/草稿区/tool_call 剥离后为空，且无命令证据。\\n'
                     '可能形态：整段思考块 / 纯空白。请复查端点输出。')

    DONE_DIR.mkdir(exist_ok=True)
    result_path = DONE_DIR / f'{name}.result.md'
    result_path.write_text(
        redact(
            f'<!-- 任务 {name} 完成于 {datetime.now():%Y-%m-%d %H:%M:%S} -->\\n\\n{reply}\\n{exec_log}\\n'
        ),
        encoding='utf-8',
    )
    shutil.move(str(task_path), str(DONE_DIR / name))
    log(f'TASK DONE    {name} -> done/{name}.result.md')'''


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

    if NEW in text:
        print('  [already] v3.7.3 两阶段研究模式（已修复，跳过）')
    elif OLD in text:
        if text.count(OLD) != 1:
            print(f'ABORT: 锚点出现 {text.count(OLD)} 次（应 1 次），未写回')
            sys.exit(1)
        text = text.replace(OLD, NEW, 1)
        print('  [patched] v3.7.3 智能两阶段研究模式')
    else:
        print('ABORT: 原锚点未找到（可能已修复或已漂移），未写回；勿重启。')
        sys.exit(1)

    TARGET.write_text(text, encoding='utf-8')
    try:
        py_compile.compile(str(TARGET), doraise=True)
        print(f'PYCOMPILE OK -> {TARGET}')
    except py_compile.PyCompileError as e:
        print(f'PYCOMPILE FAIL: {e}')
        print(f'回滚命令: cp "{BACKUP}" "{TARGET}"')
        sys.exit(3)
    print('DONE: v3.7.3 补丁应用成功（未重启；按部署铁律先 restart 后派发验证）')


if __name__ == '__main__':
    main()
