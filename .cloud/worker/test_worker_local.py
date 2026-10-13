# -*- coding: utf-8 -*-
"""worker.py v3.6 本地单测：语法 + detect_model 分级 + 黑名单命中 + 凭据出口脱敏
+ 模型映射刷新回归 + 思考块剥离 + 流式聚合三分支 + 开机记忆 ONBOARDING 加载
+ draft 两区剥离 + backlog 解析 + 自主配额 + 双指南加载 + 自动派发"""
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

# 9. 开机记忆 ONBOARDING 加载（v3.5：启动时拼进 system prompt，缺失/读失败降级不崩）
_old_ob = w.ONBOARDING_FILE
with tempfile.NamedTemporaryFile('w', suffix='.md', delete=False, encoding='utf-8') as _f:
    _f.write('# 山水工程 AI Worker · 入职指南\n\n## 4. 权限矩阵（v4 超级用户版）\n测试内容')
    _tmp_ob = _f.name
with tempfile.TemporaryDirectory() as _tmp_dir:
    try:
        # 9a. 文件在 → 全文返回
        w.ONBOARDING_FILE = pathlib.Path(_tmp_ob)
        _ob = w.load_onboarding()
        assert '入职指南' in _ob and '权限矩阵' in _ob, _ob
        print('[9] load_onboarding 文件在: PASS')
        # 9b. build_system_prompt：内置 + ONBOARDING 拼接，字符数 > 0
        _p, _n, _ = w.build_system_prompt()
        assert _n == len(_ob) and _n > 0
        assert '铁律' in _p and '入职指南' in _p, '拼接后应同时含内置铁律与入职指南'
        print('[9b] build_system_prompt 拼接（内置+ONBOARDING）: PASS')
        # 9c. 文件缺失 → '' + 降级为内置 prompt，不崩
        w.ONBOARDING_FILE = pathlib.Path(_tmp_dir) / 'no-such-onboarding.md'
        assert w.load_onboarding() == ''
        _p2, _n2, _ = w.build_system_prompt()
        assert _n2 == 0 and _p2 == w.SYSTEM_PROMPT, '缺失时应降级为内置 prompt'
        print('[9c] ONBOARDING 缺失降级（不崩）: PASS')
        # 9d. 路径是目录（读失败）→ '' 安全降级
        w.ONBOARDING_FILE = pathlib.Path(_tmp_dir)
        assert w.load_onboarding() == '', '目录路径应安全返回空'
        print('[9d] ONBOARDING 读失败降级: PASS')
    finally:
        w.ONBOARDING_FILE = _old_ob
        os.unlink(_tmp_ob)

# 10. draft 两区剥离（v3.6 机器码协议：草稿区自用存档，正式区才进 result）
_t = '<draft>自用压缩思考：mask=0x7F.. 假设A错，走B</draft>\n\n【结论】正式中文结论。'
_final, _dr = w.strip_draft(_t)
assert '【结论】' in _final and 'draft' not in _final and '假设A' not in _final, _final
assert '假设A' in _dr
_final2, _dr2 = w.strip_draft('无标记全文')
assert _final2 == '无标记全文' and _dr2 == ''
_final3, _dr3 = w.strip_draft('<draft>第一段</draft>\n中间\n<draft>第二段</draft>\n结尾')
assert '第一段' in _dr3 and '第二段' in _dr3 and 'draft' not in _final3, (_final3, _dr3)
print('[10] strip_draft 草稿区剥离（含无标记容错/多区）: PASS')

# 11. backlog 解析（v3.6：跳过已完成/阻塞也认/缺失安全）
_old_bl = w.BACKLOG_FILE
with tempfile.NamedTemporaryFile('w', suffix='.md', delete=False, encoding='utf-8') as _f:
    _f.write('# 队列\n\n1. [✔] 已完成项\n2. [ ] 未开始项A\n3. [~] 进行中项B\n4. [!] 阻塞项C\n')
    _tmp_bl = _f.name
try:
    w.BACKLOG_FILE = pathlib.Path(_tmp_bl)
    assert w.next_backlog_item() == '未开始项A', w.next_backlog_item()
    pathlib.Path(_tmp_bl).write_text('1. [✔] a\n2. [!] b（卡住）\n', encoding='utf-8')
    assert w.next_backlog_item() == 'b（卡住）', '阻塞项也应可被重试'
    pathlib.Path(_tmp_bl).write_text('1. [✔] a\n2. [✔] b\n', encoding='utf-8')
    assert w.next_backlog_item() is None, '全部完成应返回 None'
    w.BACKLOG_FILE = pathlib.Path(_tmp_bl + '.nope')
    assert w.next_backlog_item() is None, '文件缺失应安全 None'
    print('[11] next_backlog_item（跳过已完成/认阻塞/缺失安全）: PASS')
finally:
    w.BACKLOG_FILE = _old_bl
    os.unlink(_tmp_bl)

# 12. 自主配额（v3.6：AUTONOMY_BUDGET 每日计数，0=关闭，计数故障不堵生产）
_old_adir = w.AUTONOMY_DIR
with tempfile.TemporaryDirectory() as _ad:
    w.AUTONOMY_DIR = pathlib.Path(_ad)
    try:
        os.environ['AUTONOMY_BUDGET'] = '0'
        assert w.autonomy_budget_left() is False, 'BUDGET=0 应关闭自主模式'
        os.environ['AUTONOMY_BUDGET'] = '2'
        assert w.autonomy_budget_left() is True
        w.autonomy_tick()
        w.autonomy_tick()
        assert w.autonomy_budget_left() is False, '用尽应关闭'
        os.environ['AUTONOMY_BUDGET'] = 'not-a-number'
        assert w.autonomy_budget_left() is True, '非法值回落默认 12'
        print('[12] autonomy_budget 配额（0=关闭/计数用尽/非法值回落）: PASS')
    finally:
        w.AUTONOMY_DIR = _old_adir
        os.environ.pop('AUTONOMY_BUDGET', None)

# 13. 双指南加载（v3.6：ONBOARDING + AUTONOMY 拼接，缺一/全缺降级不崩；v3.7：PROMPT 亦 mock）
_old_ob, _old_au, _old_pf = w.ONBOARDING_FILE, w.AUTONOMY_FILE, w.PROMPT_FILE
with tempfile.TemporaryDirectory() as _gd:
    _ob_p = pathlib.Path(_gd) / 'ONBOARDING.md'
    _au_p = pathlib.Path(_gd) / 'AUTONOMY.md'
    w.PROMPT_FILE = pathlib.Path(_gd) / 'no-prompt.md'   # v3.7：全缺断言需 PROMPT 也不存在
    _ob_p.write_text('指南A：权限矩阵', encoding='utf-8')
    _au_p.write_text('宪章B：自主模式', encoding='utf-8')
    try:
        w.ONBOARDING_FILE, w.AUTONOMY_FILE = _ob_p, _au_p
        _g, _n, _ = w.load_guides()
        assert '指南A' in _g and '宪章B' in _g and _n > 0
        assert w.build_system_prompt()[0].startswith(w.SYSTEM_PROMPT), '内置 prompt 须在前'
        _au_p.unlink()
        _g2, _, _ = w.load_guides()
        assert '指南A' in _g2 and '宪章B' not in _g2, '缺 AUTONOMY 应只剩 ONBOARDING'
        _ob_p.unlink()
        assert w.load_guides() == ('', 0, []), '全缺应返回空'
        assert w.build_system_prompt() == (w.SYSTEM_PROMPT, 0, []), '全缺应降级内置 prompt'
        print('[13] load_guides 双文件（拼接/缺一降级/全缺降级）: PASS')
    finally:
        w.ONBOARDING_FILE, w.AUTONOMY_FILE, w.PROMPT_FILE = _old_ob, _old_au, _old_pf

# 14. 自动派发 spawn_auto_task（v3.6：PROJECT 续作优先 > backlog；配额尽/backlog 尽 → None）
_old_base, _old_tasks, _old_bl2, _old_adir2, _old_log = w.BASE, w.TASKS_DIR, w.BACKLOG_FILE, w.AUTONOMY_DIR, w.log
with tempfile.TemporaryDirectory() as _sd:
    w.BASE = pathlib.Path(_sd)
    w.TASKS_DIR = w.BASE / 'tasks'
    w.TASKS_DIR.mkdir()
    w.AUTONOMY_DIR = w.BASE / 'logs' / 'autonomy'
    w.BACKLOG_FILE = w.BASE / 'research-backlog.md'
    w.log = lambda msg: None   # 本地无日志目录，静音
    try:
        w.BACKLOG_FILE.write_text('1. [ ] Tectonic final_density 语义取证\n2. [ ] v6 三区缝合风险\n', encoding='utf-8')
        os.environ['AUTONOMY_BUDGET'] = '5'
        _n1 = w.spawn_auto_task()
        assert _n1 and 'Tectonic' in (w.TASKS_DIR / _n1).read_text(encoding='utf-8'), _n1
        assert w.autonomy_budget_left() is True, '派 1 次后配额应还剩'
        # 建 PROJECT PLAN.md → 续作优先于 backlog
        (w.BASE / 'work' / 'mask-sched').mkdir(parents=True)
        (w.BASE / 'work' / 'mask-sched' / 'PLAN.md').write_text(
            '# PLAN\n- [x] 步骤1 摸底\n- [ ] 步骤2 设计掩码函数\n- [ ] 步骤3 验证\n', encoding='utf-8')
        _n2 = w.spawn_auto_task()
        assert _n2 and 'proj-mask-sched' in _n2, _n2
        _body2 = (w.TASKS_DIR / _n2).read_text(encoding='utf-8')
        assert '步骤2' in _body2, _body2
        # backlog 尽 + 无 PLAN 未勾选 → None（不刷屏）
        (w.BASE / 'work' / 'mask-sched' / 'PLAN.md').write_text('- [x] 全完成\n', encoding='utf-8')
        w.BACKLOG_FILE.write_text('1. [✔] 都完成了\n', encoding='utf-8')
        assert w.spawn_auto_task() is None
        # 配额耗尽 → None
        w.BACKLOG_FILE.write_text('1. [ ] 还有货\n', encoding='utf-8')
        os.environ['AUTONOMY_BUDGET'] = '0'
        assert w.spawn_auto_task() is None, '配额 0 应停止派发'
        print('[14] spawn_auto_task（PROJECT 优先/backlog/配额尽/backlog 尽）: PASS')
    finally:
        w.BASE, w.TASKS_DIR, w.BACKLOG_FILE, w.AUTONOMY_DIR, w.log = _old_base, _old_tasks, _old_bl2, _old_adir2, _old_log
        os.environ.pop('AUTONOMY_BUDGET', None)

print('\nALL LOCAL TESTS PASS (v3.6: +draft 剥离/backlog/配额/双指南/自动派发)')
sys.exit(0)