<!-- 任务 2026-10-14-stream-verify.md 完成于 2026-10-14 04:21:57 -->

【结论】无法概括 `STATE.md`：现有取证未包含 `/home/agent/STATE.md` 前 20 行，不能臆造内容。

检索结果仅证明 worker 的任务队列、结果归档与日志路径配置，无法验证该文件内容或流式链路状态。建议补读该文件前 20 行后再判。

---
（据 worker 确定性侦察取证合成，检索命中见下）
/home/agent/Shanshui/.env.template:1:# .env.template — 部署时复制为 /home/agent/.env 并填入真实值（chmod 600，永不进 git）
/home/agent/Shanshui/06-archive/workbuddy-2026-10-13/worker-test-v375b.py.bak-pre-v375:7:  1. 轮询 /home/agent/tasks/ 下的 .md 任务文件（一个文件 = 一个任务）
/home/agent/Shanshui/06-archive/workbuddy-2026-10-13/worker-test-v375b.py.bak-pre-v375:9:  3. 产出存档到 /home/agent/done/<任务名>.result.md，任务原件移入 done/ 归档
/home/agent/Shanshui/06-archive/workbuddy-2026-10-13/worker-test-v375b.py.bak-pre-v375:10:  4. 全程写日志 /home/agent/logs/worker.log（logrotate 按天轮转）
/home/agent/Shanshui/06-archive/workbuddy-2026-10-13/worker-test-v375b.py.bak-pre-v375:16:  - v3.5 开机记忆：启动时读 /home/agent/ONBOARDING.md（入职指南）拼进 system prompt；
/home/agent/Shanshui/06-archive/workbuddy-2026-10-13/worker-test-v375b.py.bak-pre-v375:18:  - v3.6 自主模式：启动时增读 /home/agent/AUTONOMY.md（自主宪章）；tasks/ 空时按优先级
/home/agent/Shanshui/06-archive/workbuddy-2026-10-13/worker-test-v375b.py.bak-pre-v375:39:BASE = Path('/home/agent')
/home/agent/Shanshui/06-archive/workbuddy-2026-10-13/worker-test-v375b.py.bak-pre-v375:75:    # 递归删除系统级路径（agent 本无权限，双保险）
/home/agent/Shanshui/06-archive/workbuddy-2026-10-13/worker-test-v375b.py.bak-pre-v375:77:    'rm -rf /var', 'rm -rf /home', 'rm -rf /boot', 'rm -rf /opt',
/home/agent/Shanshui/06-archive/workbuddy-2026-10-13/worker-test-v375b.py.bak-pre-v375:78:    'rm -rf /root', 'rm -rf ~/.ssh', 'rm -rf $home/.ssh',
/home/agent/Shanshui/06-archive/workbuddy-2026-10-13/worker-test-v375b.py.bak-pre-v375:81:    '> /root', '> /home/ubuntu', '>> /home/ubuntu', 'tee /etc', 'tee -a /etc',
/home/agent/Shanshui/06-archive/workbuddy-2026-10-13/worker-test-v375b.py.bak-pre-v375:85:    'ssh-keygen', '> ~/.ssh', '>> ~/.ssh', '> /home/', '>> /home/',
/home/agent/Shanshui/06-archive/workbuddy-2026-10-13/worker-test-v375b.py.bak-pre-v375:100:    '/home/agent/.env', '~/.env', '$home/.env', 'cat .env', 'msmtprc', '.tccli',
/home/agent/Shanshui/06-archive/workbuddy-2026-10-13/worker-test-v375b.py.bak-pre-v375:106:# 任务文件头部写 `model: lite` 用轻量模型（跑腿/日志/机械劳动），
/home/agent/Shanshui/06-archive/workbuddy-2026-10-13/worker-test-v375b.py.bak-pre-v375:114:        'lite': os.environ.get('ARK_MODEL_LITE', 'doubao-lite-32k'),
/home/agent/Shanshui/06-archive/workbuddy-2026-10-13/worker-test-v375b.py.bak-pre-v375:328:    """任务头部 `model: lite/pro` 分级调度，缺省 pro"""
/home/agent/Shanshui/06-archive/workbuddy-2026-10-13/worker-test-v375b.py.bak-pre-v375:702:        lines += [f'## {p.name}', f'路径：{p}', '```markdown', head, '```', '']
/home/agent/Shanshui/06-archive/workbuddy-2026-10-13/worker-deployed.py:7:  1. 轮询 /home/agent/tasks/ 下的 .md 任务文件（一个文件 = 一个任务）
/home/agent/Shanshui/06-archive/workbuddy-2026-10-13/worker-deployed.py:9:  3. 产出存档到 /home/agent/done/<任务名>.result.md，任务原件移入 done/ 归档
/home/agent/Shanshui/06-archive/workbuddy-2026-10-13/worker-deployed.py:10:  4. 全程写日志 /home/agent/logs/worker.log（logrotate 按天轮转）

