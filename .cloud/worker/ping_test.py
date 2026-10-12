"""方舟连通性测试（agent 身份、venv312 内运行）
复用生产路径验证：import 部署版 worker → load_env → get_client → detect_model →
chat.completions.create ping。任一环断裂即点火失败。
"""
import sys

sys.path.insert(0, '/home/agent/worker')
import worker as w  # noqa: E402  部署版 worker.py（v3.2：load_env 刷新 MODEL_MAP）

w.load_env()

from openai import OpenAI  # noqa: E402

client = w.get_client()
assert client, 'get_client 返回 None（ARK_API_KEY 未加载进 os.environ）'

model = w.detect_model('model: pro\n')
print('MODEL_USED:', model)  # endpoint id（ep-xxxx），非敏感

r = client.chat.completions.create(
    model=model,
    messages=[{'role': 'user', 'content': 'ping'}],
    max_tokens=10,
)
reply = (r.choices[0].message.content or '').strip()
print('PING_REPLY:', reply)
print('USAGE:', r.usage.total_tokens if r.usage else '?')
assert reply, '回复为空'
print('PING_OK')
