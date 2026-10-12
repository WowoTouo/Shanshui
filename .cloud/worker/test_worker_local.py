# -*- coding: utf-8 -*-
"""worker.py v3.1 本地单测：语法 + detect_model 分级 + 黑名单命中 + 凭据出口脱敏"""
import importlib.util
import py_compile
import sys

SRC = r'D:\窝窝头的1.20.2整合包\Shanshui\.cloud\worker\worker.py'

# 1. 语法编译
py_compile.compile(SRC, doraise=True)
print('[1] py_compile: PASS')

spec = importlib.util.spec_from_file_location('worker', SRC)
w = importlib.util.module_from_spec(spec)
spec.loader.exec_module(w)

# 2. detect_model 分级（5 分支）
cases = [
    ('model: lite\n\n正文', w.MODEL_MAP['lite'], 'lite 显式'),
    ('model: pro\n\n正文', w.MODEL_MAP['pro'], 'pro 显式'),
    ('没有 model 头\n\n正文', w.MODEL_MAP['pro'], '缺省回落 pro'),
    ('model: LITE\n\n正文', w.MODEL_MAP['lite'], '大小写不敏感'),
    ('model: turbo\n\n正文', w.MODEL_MAP['pro'], '未知级别回落 pro'),
]
for content, expect, desc in cases:
    got = w.detect_model(content)
    assert got == expect, f'{desc}: got={got} expect={expect}'
    print(f'[2] detect_model {desc}: {got} PASS')

# 3. 黑名单命中（不真正执行子进程，只测 BLOCKED 分支）
blocked_cases = [
    'reboot',
    'rm -rf /etc',
    'systemctl restart ssh',
    'apt remove nginx',
    'shutdown -h now',
    'mkfs.ext4 /dev/sda1',
    # v3.1 凭据读取类（总工提醒：凭据资产保护）
    'cat /home/agent/.env',
    'cat ~/.env',
    'grep MAIL_PASS ~/.env',
    'cat ~/.msmtprc',
    'ls ~/.tccli/default.credential',
    'printenv',
    'cat /proc/self/environ',
]
for cmd in blocked_cases:
    ok, out = w.execute_shell(cmd)
    assert not ok, f'未拦截: {cmd}'
    assert 'BLOCKED' in out, f'拦截信息异常: {cmd} -> {out}'
    print(f'[3] FORBIDDEN "{cmd}": {out} PASS')

# 4. 铁律六条 + token 分级配置在位
assert '只做任务里指派的事' in w.SYSTEM_PROMPT
assert '不改架构' in w.SYSTEM_PROMPT
assert '只读' in w.SYSTEM_PROMPT
assert '落仓库' in w.SYSTEM_PROMPT
assert '重大变更先出方案' in w.SYSTEM_PROMPT
assert '凭据保护' in w.SYSTEM_PROMPT          # v3.1 第六条
assert w.MODEL_MAP['lite'] and w.MODEL_MAP['pro']
print('[4] SYSTEM_PROMPT 铁律六条 + MODEL_MAP: PASS')

# 5. 凭据出口脱敏 redact（v3.1 第四层防线）
w.SECRETS.clear()
w.SECRETS.append('FAKE-ARK-KEY-0123456789abcdef')
assert w.redact('Authorization: FAKE-ARK-KEY-0123456789abcdef') == 'Authorization: ***'
assert w.redact('两处 FAKE-ARK-KEY-0123456789abcdef 和 FAKE-ARK-KEY-0123456789abcdef 都打码') == '两处 *** 和 *** 都打码'
assert w.redact('chn_wwt@outlook.com 邮箱不脱敏') == 'chn_wwt@outlook.com 邮箱不脱敏'
assert w.redact('') == ''
assert w.redact('普通文本原样返回') == '普通文本原样返回'
w.SECRETS.clear()
assert w.redact('SECRETS 空时原样返回') == 'SECRETS 空时原样返回'
assert set(w.SENSITIVE_KEYS) == {'ARK_API_KEY', 'GITHUB_TOKEN', 'MAIL_PASS', 'FEISHU_WEBHOOK'}
print('[5] redact 出口脱敏 + SENSITIVE_KEYS: PASS')

# 6. load_env 后 MODEL_MAP 刷新回归（2026-10-13 404 踩坑：import 期冻结，.env 的 endpoint id 不生效）
import os
import pathlib
import tempfile

_old_map = dict(w.MODEL_MAP)
_old_env_file = w.ENV_FILE
with tempfile.NamedTemporaryFile('w', suffix='.env', delete=False, encoding='utf-8') as _f:
    _f.write('ARK_MODEL_PRO=ep-regression-pro\nARK_MODEL_LITE=ep-regression-lite\n')
    _tmp_env = _f.name
try:
    for _k in ('ARK_MODEL_PRO', 'ARK_MODEL_LITE', 'ARK_MODEL'):
        os.environ.pop(_k, None)
    w.ENV_FILE = pathlib.Path(_tmp_env)
    w.load_env()
    assert w.MODEL_MAP['pro'] == 'ep-regression-pro', f"load_env 未刷新 pro: {w.MODEL_MAP['pro']}"
    assert w.MODEL_MAP['lite'] == 'ep-regression-lite', f"load_env 未刷新 lite: {w.MODEL_MAP['lite']}"
    assert w.detect_model('正文无 model 头') == 'ep-regression-pro', 'detect_model 未用刷新后的映射'
    print('[6] load_env 刷新 MODEL_MAP（404 回归）: PASS')
finally:
    w.ENV_FILE = _old_env_file
    w.MODEL_MAP = _old_map
    for _k in ('ARK_MODEL_PRO', 'ARK_MODEL_LITE', 'ARK_MODEL'):
        os.environ.pop(_k, None)
    os.unlink(_tmp_env)

print('\nALL LOCAL TESTS PASS (v3.2: 凭据保护三层 + redact 兜底 + 模型映射刷新回归)')
sys.exit(0)
