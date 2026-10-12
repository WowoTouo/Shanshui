"""openai 大版本升级冒烟测试（不触网，agent venv312 内运行）
背景：venv 内 openai 2.20.0 -> 3.29.0（大版本跨越），worker.py 调用面需验证：
  1. from openai import OpenAI + OpenAI(base_url=, api_key=) 构造
  2. client.chat.completions.create(model/messages/temperature/max_tokens)
  3. resp.choices[0].message.content（ChatCompletion/Choice/Message 字段）
  4. resp.usage.total_tokens（CompletionUsage 字段）
退出码：0 = SMOKE_OK；1 = SMOKE_FAIL（附缺失明细）
"""
import inspect
import sys

import openai
from openai import OpenAI
from openai.types.chat import ChatCompletion
from openai.types.chat.chat_completion_message import ChatCompletionMessage
from openai.types.completion_usage import CompletionUsage

fails = []
print(f"openai version: {openai.__version__}")

# 1+2. 构造与 create 签名（构造不触网）
client = OpenAI(base_url="https://example.invalid", api_key="dummy-not-used")
print("OpenAI(base_url=, api_key=) 构造: OK")

need = {"model", "messages", "temperature", "max_tokens"}
missing = need - set(inspect.signature(client.chat.completions.create).parameters)
if missing:
    fails.append(f"create() 缺少参数: {sorted(missing)}")
else:
    print(f"create() 参数齐全: {sorted(need)}")

# 3. 响应字段
cc_fields = set(ChatCompletion.model_fields)
for f in ("choices", "usage"):
    if f not in cc_fields:
        fails.append(f"ChatCompletion 缺字段: {f}")
print(f"ChatCompletion.choices/usage: {'OK' if 'choices' in cc_fields and 'usage' in cc_fields else 'MISSING'}")

if "content" not in ChatCompletionMessage.model_fields:
    fails.append("ChatCompletionMessage 缺 content 字段")
else:
    print("ChatCompletionMessage.content: OK")

# 4. usage.total_tokens
if "total_tokens" not in CompletionUsage.model_fields:
    fails.append("CompletionUsage 缺 total_tokens 字段")
else:
    print("CompletionUsage.total_tokens: OK")

if fails:
    print("SMOKE_FAIL")
    for f in fails:
        print(" -", f)
    sys.exit(1)
print("SMOKE_OK")
