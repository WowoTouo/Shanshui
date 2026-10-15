<!-- 任务 test-004-self-diagnosis.md 完成于 2026-10-15 06:40:34 -->

【结论】零正文是格式性空响应：复杂编码任务触发“强沉默+仅输出文件+思考/draft剥离”，而非模型能力故障。

test-002 是摘要任务，可直接成文；test-003 写码时，DLC-003 要求“只输出目标文件、块外无解释”，但任务未给路径，模型可能把内容全放入 think/draft 或等待 FILE 头，剥离后 phase1=0。“默认沉默、不产出回答型内容”也被误读为“不返回正文”。

建议：①声明“沉默指不主动打扰，非空回复”；②编码任务强制“【结论】+内联代码块”，无路径也输出；③剥离前保存 raw，phase1=0 时带“禁止空响应”重试；④核查 max_tokens/stop。

诊断：复杂任务诱发过度自抑和文件-only模式，剥离后只剩空壳。

---
（据 worker 确定性侦察取证合成，检索命中见下）
_layers)} -> system prompt（四层开机记忆生效）')
/home/agent/Shanshui/06-archive/workbuddy-2026-10-13/.workbuddy/memory/2026-10-13.md:187:- **连通测试 PING_OK**：ping_test.py 复用生产路径（import 部署版 worker → load_env → get_client → detect_model → create），ep 端点返回真实内容（154 tokens）
/home/agent/Shanshui/06-archive/workbuddy-2026-10-13/.workbuddy/memory/2026-10-13.md:188:- **first-task 闭环达成**：07:16:52 TASK START（tectonic-final-density，792 chars）→ 07:17:02 TASK LLM OK（1209 tokens）→ EXEC 1 命令 ok=True → TASK DONE 归档 done/*.result.md
/home/agent/Shanshui/06-archive/workbuddy-2026-10-13/.workbuddy/memory/2026-10-13.md:189:- **测试任务闭环**：readme-summary-test → TASK DONE（869 tokens）；模型正确拒编（未提供文件内容 + 不许执行命令 → 拒绝臆造），是好评行为；v3.3 思考块剥离实证生效（result 无 seed:think 噪声）
/home/agent/Shanshui/06-archive/workbuddy-2026-10-13/.workbuddy/memory/2026-10-13.md:204:- **worker.py v3.5 开机记忆**：`load_onboarding()` + `build_system_prompt()` + `SYSTEM_PROMPT_EFFECTIVE` 进程内固定（只读一次保上下文缓存）；main() load_env 后刷新，日志 `ONBOARDING loaded (4201 chars)`；缺失/读失败降级不崩（单测 [9]/[9b]/[9c]/[9d]，本地 29 项全过）
/home/agent/Shanshui/06-archive/workbuddy-2026-10-13/.workbuddy/memory/2026-10-13.md:214:- **服务器 AI 恢复执行能力**：SSH 重置被烧穿的 autonomy 配额（count=12→重置 0）、`sudo systemctl restart ai-worker`；重启后日志 `=== worker process start ===` + `GUIDES loaded (10362 chars) -> system prompt（开机记忆生效）` + `AUTO SPAWN` 正常派发 → 执行能力恢复（仍 v3.6，未部署 v3.7；v3.7 部署需先本地跑 patch_v37.py + 40 项测试再走 §8 顺序）
/home/agent/Shanshui/06-archive/workbuddy-2026-10-13/.workbuddy/memory/2026-10-13.md:333:  - PASS(8)：存活 / 四层注入(GUIDES 15367 chars) / 三件套 / 端点响应 / 邮件脚本 / 目录 / 协调文件 / 配额守卫(bal 4963479→4947479 增量正确扣 2×8000)。
/home/agent/Shanshui/06-archive/workbuddy-2026-10-13/.workbuddy/memory/2026-10-13.md:360:- 实证：模型零产出（phase1_len=0）下，v3.7.5 worker 自侦察→合成 727 字诚实结论（认定证据不足不臆断 + 给原版机制 + 下一步反编译 jar），已上云 research/results/v375。
/home/agent/Shanshui/06-archive/workbuddy-2026-10-13/.workbuddy/memory/2026-10-13.md:376:- 下一步(未做)：① 完整 systemd unit diff(live vs repo)抓其它潜在漂移；② 真正容器/WSL dry-run(需用户环境或一次性免费服务器)，顺便验证 test_worker_local.py 在干净 3.12.15 环境 ALL PASS；③ GitHub 仍待镜像泵窗口。
/home/agent/Shanshui/06-archive/workbuddy-2026-10-13/.workbuddy/memory/MEMORY.md:37:- **版本真相（2026-10-13 20:0x 更新）**：**服务器现跑 v3.7 四层注入版**——GUIDES loaded 15367 chars（PROMPT+ONBOARDING+AUTONOMY+DLC-001），三件套（STALL守卫/清理循环/提案通道）均在位（worker.py md5 61d1728b）；历史包袱：本地 v3.6 半补丁（md5 d08ee64）禁部署；v3.7 经 patch_v37.py + 三方协作落地
/home/agent/Shanshui/06-archive/workbuddy-2026-10-13/worker-test-v375.py.bak-pre-v375:165:【项目背景】
/home/agent/Shanshui/06-archive/workbuddy-2026-10-13/worker-test-v375.py.bak-pre-v375:373:    log(f'TASK START  {name} ({len(content)} chars)')
/home/agent/Shanshui/06-archive/workbuddy-2026-10-13/worker-test-v375.py.bak-pre-v375:398:    log(f'TASK LLM OK  {name} | model={model} tokens={tokens if tokens else "?"} phase1_len={len(reply)}')
/home/agent/Shanshui/06-archive/workbuddy-2026-10-13/worker-test-v375.py.bak-pre-v375:731:        log(f'GUIDES loaded ({_guide_len} chars): {" + ".join(_layers)} -> system prompt（四层开机记忆生效）')

