import os
from openai import OpenAI
for line in open('/home/agent/.env', encoding='utf-8'):
    line = line.strip()
    if line and not line.startswith('#') and '=' in line:
        k, v = line.split('=', 1)
        os.environ.setdefault(k, v)
c = OpenAI(base_url=os.environ['ARK_BASE_URL'], api_key=os.environ['ARK_API_KEY'])
m = os.environ.get('ARK_MODEL_PRO') or os.environ.get('ARK_MODEL_LITE')
msg = [{'role': 'user', 'content': '请只回复两个字：正常'}]
r = c.chat.completions.create(model=m, messages=msg, max_tokens=200)
nc = r.choices[0].message.content or ''
print('NONSTREAM len=%d snippet=%r' % (len(nc), nc[:150]))
s = c.chat.completions.create(model=m, messages=msg, max_tokens=200, stream=True)
buf = ''
for ch in s:
    try:
        d = ch.choices[0].delta
        if d and d.content:
            buf += d.content
    except Exception:
        pass
print('STREAM    len=%d snippet=%r' % (len(buf), buf[:150]))
