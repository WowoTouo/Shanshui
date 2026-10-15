<!-- 任务 test-001-normal-flow.md 完成于 2026-10-15 05:58:34 -->

【结论】无法完成提取：现有取证未包含 `/opt/shanshui/README.md` 内容，也未出现“五层管控速查表”，因此不能据此生成或写入 `research/drafts/test-001-result.md`。

检索结果仅涉及 worker 源码中的 `model: lite` 调度、`<draft>` 剥离、`research-backlog.md` 解析等机制，与目标速查表无关。为避免编造数据，需补充读取该 README 原文或提供相关段落后，才能提取并落盘。

---
（据 worker 确定性侦察取证合成，检索命中见下）
/home/agent/Shanshui/.env.template:2:# 真实值见加密包 secrets.zip（密码在本地 README-SECRET.txt）
/home/agent/Shanshui/06-archive/workbuddy-2026-10-13/worker-test-v375b.py.bak-pre-v375:53:BACKLOG_FILE = BASE / 'research-backlog.md' # v3.6 研究方向队列（总工维护，AI 更新状态）
/home/agent/Shanshui/06-archive/workbuddy-2026-10-13/worker-test-v375b.py.bak-pre-v375:106:# 任务文件头部写 `model: lite` 用轻量模型（跑腿/日志/机械劳动），
/home/agent/Shanshui/06-archive/workbuddy-2026-10-13/worker-test-v375b.py.bak-pre-v375:114:        'lite': os.environ.get('ARK_MODEL_LITE', 'doubao-lite-32k'),
/home/agent/Shanshui/06-archive/workbuddy-2026-10-13/worker-test-v375b.py.bak-pre-v375:159:    drafts = re.findall(r'<draft>(.*?)</draft>', text, flags=re.DOTALL)
/home/agent/Shanshui/06-archive/workbuddy-2026-10-13/worker-test-v375b.py.bak-pre-v375:161:    return final, '\n\n---\n\n'.join(d.strip() for d in drafts if d.strip())
/home/agent/Shanshui/06-archive/workbuddy-2026-10-13/worker-test-v375b.py.bak-pre-v375:328:    """任务头部 `model: lite/pro` 分级调度，缺省 pro"""
/home/agent/Shanshui/06-archive/workbuddy-2026-10-13/worker-test-v375b.py.bak-pre-v375:519:    """解析 research-backlog.md，返回第一个未完成项（[ ]/[~]/[!]）文本；尽/缺 → None。"""
/home/agent/Shanshui/06-archive/workbuddy-2026-10-13/worker-test-v375b.py.bak-pre-v375:618:        slug = re.sub(r'[^\w一-龥]+', '-', item)[:40].strip('-') or 'research'
/home/agent/Shanshui/06-archive/workbuddy-2026-10-13/worker-test-v375b.py.bak-pre-v375:629:2. 完成后用 shell 块更新 research-backlog.md 状态行（[✔] 完成 / [!] 阻塞+原因）
/home/agent/Shanshui/06-archive/workbuddy-2026-10-13/worker-test-v375b.py.bak-pre-v375:743:            # 排除 README.md：任务目录的说明文件不是任务（2026-10-13 修复）
/home/agent/Shanshui/06-archive/workbuddy-2026-10-13/worker-deployed.py:53:BACKLOG_FILE = BASE / 'research-backlog.md' # v3.6 研究方向队列（总工维护，AI 更新状态）
/home/agent/Shanshui/06-archive/workbuddy-2026-10-13/worker-deployed.py:106:# 任务文件头部写 `model: lite` 用轻量模型（跑腿/日志/机械劳动），
/home/agent/Shanshui/06-archive/workbuddy-2026-10-13/worker-deployed.py:114:        'lite': os.environ.get('ARK_MODEL_LITE', 'doubao-lite-32k'),
/home/agent/Shanshui/06-archive/workbuddy-2026-10-13/worker-deployed.py:159:    drafts = re.findall(r'<draft>(.*?)</draft>', text, flags=re.DOTALL)
/home/agent/Shanshui/06-archive/workbuddy-2026-10-13/worker-deployed.py:161:    return final, '\n\n---\n\n'.join(d.strip() for d in drafts if d.strip())
/home/agent/Shanshui/06-archive/workbuddy-2026-10-13/worker-deployed.py:328:    """任务头部 `model: lite/pro` 分级调度，缺省 pro"""
/home/agent/Shanshui/06-archive/workbuddy-2026-10-13/worker-deployed.py:484:    """解析 research-backlog.md，返回第一个未完成项（[ ]/[~]/[!]）文本；尽/缺 → None。"""
/home/agent/Shanshui/06-archive/workbuddy-2026-10-13/worker-deployed.py:583:        slug = re.sub(r'[^\w一-龥]+', '-', item)[:40].strip('-') or 'research'
/home/agent/Shanshui/06-archive/workbuddy-2026-10-13/worker-deployed.py:594:2. 完成后用 shell 块更新 research-backlog.md 状态行（[✔] 完成 / [!] 阻塞+原因）

