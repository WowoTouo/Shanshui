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
task2 = ('研究任务：Tectonic final_density 语义取证。\n'
         '已通过命令取证，获得以下证据（勿再执行命令，直接据下列证据写结论）：\n'
         '- 证据1：Tectonic 中 final_density 是 density function 流水线终点，输入为多源噪声/地形权重叠加，输出经 clamp 到约 [-1.0, 1.0] 后交 terrain_shaper\n'
         '- 证据2：该值位于世界生成 density function 层，理论上可被外部数据包/density function 覆写\n\n'
         '请基于以上证据，用中文正文直接输出结论：输入语义、输出语义、取值范围、能否被外部调度器改写。结论置顶，≤300字，严禁输出工具调用。')
msgs = [{'role': 'system', 'content': prompt}, {'role': 'user', 'content': task2}]
s = c.chat.completions.create(model=m, messages=msgs, temperature=0.3, max_tokens=1024, stream=True)
buf = ''
for ch in s:
    try:
        d = ch.choices[0].delta
        if getattr(d, 'content', None):
            buf += d.content
    except Exception:
        pass
print('SYNTH content len=%d' % len(buf))
print('SYNTH snippet=%r' % buf[:350])
