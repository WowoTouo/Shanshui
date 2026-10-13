#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""patch_v374.py — worker.py v3.7.4 两阶段合成增强
v3.7.3 只在"有命令证据(exec_log)"时触发合成；但模型有时只回 <draft> 计划（无可执行命令）
也被剥空 → 落入占位。本补丁把合成触发条件扩为 exec_log + draft 计划合并为上下文，
两种退化形态（狂调工具 / 只思考给计划）都能二阶段合成出正文结论。
"""
import sys
import shutil
import py_compile
from pathlib import Path

TARGET = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('/home/agent/worker/worker.py')
BACKUP = TARGET.parent / (TARGET.name + '.bak-pre-v374')

OLD = '''    if not reply.strip():
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
                     '可能形态：整段思考块 / 纯空白。请复查端点输出。')'''

NEW = '''    if not reply.strip():
        # 合并可用上下文：命令执行证据(exec_log) + 模型研究计划/思考(draft)
        ctx = ''
        if exec_log.strip():
            ctx += '【命令执行证据】\\n' + exec_log + '\\n'
        if draft.strip():
            ctx += '【模型研究计划/思考】\\n' + draft + '\\n'
        if ctx.strip():
            log(f'TASK SYNTH   {name} 一阶段零正文，据可用上下文二阶段合成结论')
            synth_task = (
                f'原任务：\\n{content}\\n\\n'
                f'已收集以下信息：\\n{ctx}\\n'
                '请基于以上信息，用中文正文直接输出研究结论（≤300字，结论置顶）；'
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
                    reply = '（模型未直接产出正文，以下为已收集信息）\\n' + ctx
                    log(f'TASK SYNTH EMPTY {name} 二阶段仍空，回退已收集信息')
            except Exception as e:
                log(f'TASK SYNTH ERR {name}: {type(e).__name__}: {e}')
                reply = '（二阶段合成异常，以下为已收集信息）\\n' + ctx
        else:
            # 真·无正文、无证据、无计划 → 兜底占位（绝不空白）
            log(f'TASK LLM EMPTY {name} 无正文无上下文，写兜底占位')
            reply = ('【worker 兜底】模型回复经思考块/草稿区/tool_call 剥离后为空，且无任何上下文。\\n'
                     '可能形态：纯空白。请复查端点输出。')'''


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
        print('  [already] v3.7.4 两阶段合成增强（已修复，跳过）')
    elif OLD in text:
        if text.count(OLD) != 1:
            print(f'ABORT: 锚点出现 {text.count(OLD)} 次（应 1 次），未写回')
            sys.exit(1)
        text = text.replace(OLD, NEW, 1)
        print('  [patched] v3.7.4 两阶段合成增强（exec_log+draft 合并上下文）')
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
    print('DONE: v3.7.4 补丁应用成功（未重启；按部署铁律先 restart 后派发验证）')


if __name__ == '__main__':
    main()
