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
task = open('/home/agent/done/2026-10-13-v372-fix-verify.md', encoding='utf-8').read()
s = c.chat.completions.create(model=m,
        messages=[{'role': 'system', 'content': prompt}, {'role': 'user', 'content': task}],
        temperature=0.3, max_tokens=4096, stream=True)
buf = ''
for ch in s:
    try:
        d = ch.choices[0].delta
        if d and d.content:
            buf += d.content
    except Exception:
        pass
print('RAW stream len=%d' % len(buf))
print('RAW snippet=%r' % buf[:400])
stripped = w.strip_think_tags(buf)
print('STRIPPED len=%d snippet=%r' % (len(stripped), stripped[:200]))
