import os, importlib.util
from openai import OpenAI
for line in open('/home/agent/.env', encoding='utf-8'):
    line = line.strip()
    if line and not line.startswith('#') and '=' in line:
        k, v = line.split('=', 1)
        os.environ.setdefault(k, v)
spec = importlib.util.spec_from_file_location('w', '/home/agent/worker/worker.py')
w = importlib.util.module_from_spec(spec); spec.loader.exec_module(w)
prompt, n, layers = w.build_system_prompt()
c = OpenAI(base_url=os.environ['ARK_BASE_URL'], api_key=os.environ['ARK_API_KEY'])
m = os.environ.get('ARK_MODEL_PRO')
task = ('# 研究任务：Tectonic final_density 语义取证\n'
        '请用中文正文直接给出结论：输入语义、输出语义、取值范围、能否被外部调度器改写。结论置顶，≤300字。\n\n'
        '【系统纠偏】请直接用中文正文输出研究结论；bash 命令仅用于取证且必须配正文总结；严禁整段只输出工具调用或思考块。')
msgs = [{'role': 'system', 'content': prompt}, {'role': 'user', 'content': task}]
s = c.chat.completions.create(model=m, messages=msgs, temperature=0.3, max_tokens=2048, stream=True)
buf = ''
for ch in s:
    try:
        d = ch.choices[0].delta
        if getattr(d, 'content', None):
            buf += d.content
    except Exception:
        pass
print('WITH-NUDGE stream content len=%d' % len(buf))
print('snippet=%r' % buf[:300])
stripped = w.strip_think_tags(buf)
print('stripped-prose len=%d' % len(stripped))
