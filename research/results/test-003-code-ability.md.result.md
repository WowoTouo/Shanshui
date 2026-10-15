<!-- 任务 test-003-code-ability.md 完成于 2026-10-15 06:37:54 -->

【结论】我是山水工程首席研究员 AI「Shan」，负责自主执行研究与编码任务并产出可验证结论。所给检索证据仅涉及 worker 任务轮询/归档机制，**未包含 SSGC、SSHE 的定义**，无法据实说明二者分别是什么，不臆测。计数脚本可按"读取 `/home/agent/worker/worker.py` → 正则统计行首 `def ` → 写入 `/tmp/test_shan_result.txt`"实现；但本轮要求禁止工具调用，脚本未实际执行，函数数量无法验证，需 shell 运行后才能给出真实数值。本次测试确认身份认知与取证纪律正常，项目结构理解及可执行结果待补跑验证。

---
（据 worker 确定性侦察取证合成，检索命中见下）
/home/agent/Shanshui/.env.template:1:# .env.template — 部署时复制为 /home/agent/.env 并填入真实值（chmod 600，永不进 git）
/home/agent/Shanshui/06-archive/workbuddy-2026-10-13/worker-test-v375b.py.bak-pre-v375:7:  1. 轮询 /home/agent/tasks/ 下的 .md 任务文件（一个文件 = 一个任务）
/home/agent/Shanshui/06-archive/workbuddy-2026-10-13/worker-test-v375b.py.bak-pre-v375:9:  3. 产出存档到 /home/agent/done/<任务名>.result.md，任务原件移入 done/ 归档
/home/agent/Shanshui/06-archive/workbuddy-2026-10-13/worker-test-v375b.py.bak-pre-v375:10:  4. 全程写日志 /home/agent/logs/worker.log（logrotate 按天轮转）
/home/agent/Shanshui/06-archive/workbuddy-2026-10-13/worker-test-v375b.py.bak-pre-v375:16:  - v3.5 开机记忆：启动时读 /home/agent/ONBOARDING.md（入职指南）拼进 system prompt；
/home/agent/Shanshui/06-archive/workbuddy-2026-10-13/worker-test-v375b.py.bak-pre-v375:18:  - v3.6 自主模式：启动时增读 /home/agent/AUTONOMY.md（自主宪章）；tasks/ 空时按优先级
/home/agent/Shanshui/06-archive/workbuddy-2026-10-13/worker-test-v375b.py.bak-pre-v375:39:BASE = Path('/home/agent')
/home/agent/Shanshui/06-archive/workbuddy-2026-10-13/worker-test-v375b.py.bak-pre-v375:77:    'rm -rf /var', 'rm -rf /home', 'rm -rf /boot', 'rm -rf /opt',
/home/agent/Shanshui/06-archive/workbuddy-2026-10-13/worker-test-v375b.py.bak-pre-v375:78:    'rm -rf /root', 'rm -rf ~/.ssh', 'rm -rf $home/.ssh',
/home/agent/Shanshui/06-archive/workbuddy-2026-10-13/worker-test-v375b.py.bak-pre-v375:81:    '> /root', '> /home/ubuntu', '>> /home/ubuntu', 'tee /etc', 'tee -a /etc',
/home/agent/Shanshui/06-archive/workbuddy-2026-10-13/worker-test-v375b.py.bak-pre-v375:85:    'ssh-keygen', '> ~/.ssh', '>> ~/.ssh', '> /home/', '>> /home/',
/home/agent/Shanshui/06-archive/workbuddy-2026-10-13/worker-test-v375b.py.bak-pre-v375:100:    '/home/agent/.env', '~/.env', '$home/.env', 'cat .env', 'msmtprc', '.tccli',
/home/agent/Shanshui/06-archive/workbuddy-2026-10-13/worker-test-v375b.py.bak-pre-v375:163:SYSTEM_PROMPT = """你是「山水工程 Shanshui」项目的专职 AI 代理，7×24 无人值守运行。
/home/agent/Shanshui/06-archive/workbuddy-2026-10-13/worker-deployed.py:7:  1. 轮询 /home/agent/tasks/ 下的 .md 任务文件（一个文件 = 一个任务）
/home/agent/Shanshui/06-archive/workbuddy-2026-10-13/worker-deployed.py:9:  3. 产出存档到 /home/agent/done/<任务名>.result.md，任务原件移入 done/ 归档
/home/agent/Shanshui/06-archive/workbuddy-2026-10-13/worker-deployed.py:10:  4. 全程写日志 /home/agent/logs/worker.log（logrotate 按天轮转）
/home/agent/Shanshui/06-archive/workbuddy-2026-10-13/worker-deployed.py:16:  - v3.5 开机记忆：启动时读 /home/agent/ONBOARDING.md（入职指南）拼进 system prompt；
/home/agent/Shanshui/06-archive/workbuddy-2026-10-13/worker-deployed.py:18:  - v3.6 自主模式：启动时增读 /home/agent/AUTONOMY.md（自主宪章）；tasks/ 空时按优先级
/home/agent/Shanshui/06-archive/workbuddy-2026-10-13/worker-deployed.py:39:BASE = Path('/home/agent')
/home/agent/Shanshui/06-archive/workbuddy-2026-10-13/worker-deployed.py:77:    'rm -rf /var', 'rm -rf /home', 'rm -rf /boot', 'rm -rf /opt',

