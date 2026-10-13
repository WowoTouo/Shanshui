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
print('system prompt len=%d layers=%s' % (len(prompt), layers))
c = OpenAI(base_url=os.environ['ARK_BASE_URL'], api_key=os.environ['ARK_API_KEY'])
m = os.environ.get('ARK_MODEL_PRO')
task = ('# 研究任务：Tectonic final_density 语义取证\n'
        '请用中文正文直接给出结论：输入语义、输出语义、取值范围、能否被外部调度器改写。'
        '结论置顶，≤300字，不要只发工具调用。')
msgs = [{'role': 'system', 'content': prompt}, {'role': 'user', 'content': task}]
# 1) non-streaming
r = c.chat.completions.create(model=m, messages=msgs, temperature=0.3, max_tokens=4096)
mc = r.choices[0].message
nc = mc.content or ''
print('NONSTREAM content len=%d' % len(nc))
print('NONSTREAM content snippet=%r' % nc[:250])
print('NONSTREAM has reasoning_content=%s len=%s' % (hasattr(mc, 'reasoning_content'), len(getattr(mc, 'reasoning_content', '') or '')))
# 2) streaming, capture content + reasoning_content
s = c.chat.completions.create(model=m, messages=msgs, temperature=0.3, max_tokens=4096, stream=True)
buf = ''; rbuf = ''
for ch in s:
    try:
        d = ch.choices[0].delta
        if getattr(d, 'content', None): buf += d.content
        if getattr(d, 'reasoning_content', None): rbuf += d.reasoning_content
    except Exception:
        pass
print('STREAM content len=%d reasoning len=%d' % (len(buf), len(rbuf)))
print('STREAM content snippet=%r' % buf[:200])
