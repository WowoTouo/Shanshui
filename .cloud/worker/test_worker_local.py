# -*- coding: utf-8 -*-
"""worker.py v3.4 本地单测：语法 + detect_model 分级 + 黑名单命中 + 凭据出口脱敏
+ 模型映射刷新回归 + 思考块剥离 + 流式聚合三分支"""
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

# 7. 思考块剥离（v3.3：方舟 seed 系端点把 <seed:think_*> 混进 content）
_raw = ('<seed:think_never_used_abc123>\n内部思考，含示例命令：\n```bash\nrm -rf /\n```\n'
        '</think_never_used_abc123>\n可见结论：Tectonic 的 final_density 为只读密度函数。')
_clean = w.strip_think_tags(_raw)
assert '内部思考' not in _clean and 'rm -rf' not in _clean, _clean
assert 'Tectonic' in _clean and _clean.strip().startswith('可见结论'), _clean
assert w.extract_shell_blocks(_clean) == [], '思考块内的示例命令不应被提取执行'
print('[7] strip_think_tags 思考块剥离（含防误执行）: PASS')

# 8. 流式聚合正确性（v3.4：mock chunk 迭代拼接 + stream=True 传递 + usage 缺失降级 + 中途错误上抛）
import types


def _chunk(content=None, usage=None, no_choices=False):
    c = types.SimpleNamespace()
    c.choices = [] if no_choices else [types.SimpleNamespace(delta=types.SimpleNamespace(content=content))]
    c.usage = usage
    return c


def _mock_client(chunks, capture=None):
    def _create(**kwargs):
        if capture is not None:
            capture.update(kwargs)
        return iter(chunks)
    return types.SimpleNamespace(chat=types.SimpleNamespace(completions=types.SimpleNamespace(create=_create)))


# 8a. 正常拼接 + 末 chunk 带 usage + stream=True 已传
_cap = {}
_chunks = [_chunk('你好'), _chunk('，世界'),
           _chunk(None, usage=types.SimpleNamespace(total_tokens=42), no_choices=True)]
_text, _usage = w.chat_completions_stream(_mock_client(_chunks, _cap), 'ep-test', [{'role': 'user', 'content': 'hi'}])
assert _text == '你好，世界', _text
assert _usage is not None and _usage.total_tokens == 42, _usage
assert _cap.get('stream') is True, 'create 未收到 stream=True'
assert _cap.get('temperature') == 0.3 and _cap.get('max_tokens') == 4096
print('[8] 流式聚合 + usage 末 chunk + stream=True: PASS')

# 8b. 方舟不返回 usage → None 降级（日志侧记 ?，不报错）
_text2, _usage2 = w.chat_completions_stream(
    _mock_client([_chunk('abc'), _chunk(None, no_choices=True)]), 'ep-test', [])
assert _text2 == 'abc' and _usage2 is None, (_text2, _usage2)
print('[8b] 流式无 usage 降级 None: PASS')


# 8c. 中途抛错 → 异常上抛（主循环 ERROR+退避兜底），不吞
def _boom_gen():
    yield _chunk('part')
    raise RuntimeError('mid-stream')


_mock_boom = types.SimpleNamespace(
    chat=types.SimpleNamespace(completions=types.SimpleNamespace(create=lambda **kw: _boom_gen())))
try:
    w.chat_completions_stream(_mock_boom, 'ep-test', [])
    raise AssertionError('流式中途错误未上抛')
except RuntimeError as e:
    assert 'mid-stream' in str(e), e
print('[8c] 流式中途错误上抛: PASS')

print('\nALL LOCAL TESTS PASS (v3.4: +流式聚合三分支)')
sys.exit(0)
