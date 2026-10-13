# CHRONICLE.md — 山水基石日志（完整时间戳流水档案）

> **层级定位**：FOUNDATION（协议层）· SIGNAL（机读信令层）· **本文件 = 事实档案层**
> 记录每次关键动作的完整详情（配置/部署/修复/验证/迁移/稳定节点），带精确时间戳
> **生成**：chronicle.sh 每日自动从 worker.log 提取关键事件追加；接口（科学/发展）可手动补记
> **同步**：服务器 `/home/agent/CHRONICLE.md` 为权威主文件，git 镜像 `coordination/CHRONICLE.md`，Gitee 主推 + GitHub 镜像泵
> **追加格式**：`- HH:MM 类别 | 动作详情 | 结果`

---

## 2026-10-13（历史流水，由发展接口整理补记）

### 基建期
- 18:02 部署 | Gitee runner 安装注册（/home/ubuntu/gitee-go-runner，amd64，uuid 6cf5b4c2-3b74-48e7-a73b-a31d2a636118）| 成功，服务端可连
- 18:13 部署 | gitee-github-bridge.sh 镜像泵 + agent cron */30 | 就位，TLS 窗口触发三地对齐 68b75d5
- 17:24 信令 | 总工裁定写入 SIGNAL（异步留痕非实时 / 清理脚本红线）| 三方共识
- 19:07 探测 | 方舟 API 探测：usage 端点 404（无 AK/SK 查不了精确余额），models 200 | 确认推理 key 不可查余额
- 19:2x 配置 | quota-alert.sh 额度估算监控（基准 4,963,479 tokens，单次估 8k，阈值 100 万，邮件告警）+ cron */6 | 上线
- 19:2x 迁移 | 服务器资产盘点完成：worker 纯标准库零 pip 依赖（venv312 有 aider 等辅助包但非必需）| 迁移可行性确认
- 19:25 迁移 | REBUILD.md 重建手册 + .env.template 脱敏模板 + .gitignore 加固（secrets/、*.zip、.git-credentials 永不入库）| commit 327710c 推送 Gitee
- 19:25 安全 | .env + .git-credentials 拉取 → secrets.zip 加密包（ZipCrypto + 20 位随机密码）| 存 D:\窝窝头的1.20.2整合包\Shanshui\secrets\，密码在 README-SECRET.txt
- 19:3x 配置 | chronicle.sh 基石日志生成器 + cron 每日 0 7 | 上线（本档案自动追加起点）

### 接口补记（发展，2026-10-13 晚）
- 19:30 审计 | 迁移备份一致性核验：服务器 vs 仓库 md5 全量比对（worker/指南/工具/协调文件）| 发现 3 不一致（ONBOARDING/OPS-STATE/CHRONICLE 服务器版更新）+ bak-v37 本地缺失 + 3 工具脚本（bridge/quota/chronicle）未入库 → **全部拉回对齐，以服务器实际运行为准**
- 19:3x 配置 | 基石日志系统上线：chronicle.sh（cron 0 7）+ CHRONICLE.md 档案层 | 自动提取 worker.log 关键事件；**08:12 死循环事故证据（同任务 8 秒间隔反复 START/DONE/SPAWN）已自动入档**
- 19:3x 设计 | 模型无关化：确认 worker.py OpenAI 兼容（client.chat.completions.create，stream）→ 换模型零代码（只改 .env 三键）| FOUNDATION §三 新增模型无关化条款 + MODEL-REGISTRY.md 模型记忆库（M1 当前模型记忆 + 候选白嫖清单 SiliconFlow/GLM/Qwen/DeepSeek/Kimi/Ollama + 一键切换步骤）
- 19:3x 迁移 | REBUILD.md 重建手册 + .env.template 脱敏模板 + .gitignore 加固 | commit 327710c / 93a1afd 推 Gitee；GitHub 镜像泵待窗口

### 稳定性节点
- v3.7 三件套 | STALL 守卫 / 清理循环 / 提案通道 静态核验逐行确认（_current_auto_target@460 / maybe_run_cleanup@555 / check_proposals@579）| 已落地
- 配额 | 10-13 自主配额 count 重置（旧死循环烧穿 12→0，STALL 守卫兜底后恢复）| QUOTA:0

## 2026-10-13
- [2026-10-13 07:13:48] | TASK START  2026-10-13-tectonic-final-density.md (792 chars)
- [2026-10-13 07:13:48] | ERROR 2026-10-13-tectonic-final-density.md: NotFoundError: Error code: 404 - {'error': {'code': 'InvalidEndpointOrModel.NotFound', 'message': 'The model or endpoint doubao-pro-32k does not exist or you do not have access to it. Request id: 02179184682836946c14d470d092c1c2bed457a462426b2c3605a', 'param': '', 'type': 'Not Found'}}
- [2026-10-13 07:15:48] | TASK START  2026-10-13-tectonic-final-density.md (792 chars)
- [2026-10-13 07:15:48] | ERROR 2026-10-13-tectonic-final-density.md: NotFoundError: Error code: 404 - {'error': {'code': 'InvalidEndpointOrModel.NotFound', 'message': 'The model or endpoint doubao-pro-32k does not exist or you do not have access to it. Request id: 021791846948579a92b4afba7ed5745e150097919eafbc65bcae2', 'param': '', 'type': 'Not Found'}}
- [2026-10-13 07:16:52] | TASK START  2026-10-13-tectonic-final-density.md (792 chars)
- [2026-10-13 07:17:02] | TASK LLM OK  2026-10-13-tectonic-final-density.md | model=ep-20261013070524-xjjn2 tokens=1209
- [2026-10-13 07:17:02] | TASK DONE    2026-10-13-tectonic-final-density.md -> done/2026-10-13-tectonic-final-density.md.result.md
- [2026-10-13 07:19:01] | TASK START  2026-10-13-readme-summary-test.md (131 chars)
- [2026-10-13 07:19:16] | TASK LLM OK  2026-10-13-readme-summary-test.md | model=ep-20261013070524-xjjn2 tokens=869
- [2026-10-13 07:19:16] | TASK DONE    2026-10-13-readme-summary-test.md -> done/2026-10-13-readme-summary-test.md.result.md
- [2026-10-13 07:31:16] | TASK START  2026-10-13-stream-verify.md (92 chars)
- [2026-10-13 07:31:21] | TASK LLM OK  2026-10-13-stream-verify.md | model=ep-20261013070524-xjjn2 tokens=617
- [2026-10-13 07:31:21] | TASK DONE    2026-10-13-stream-verify.md -> done/2026-10-13-stream-verify.md.result.md
- [2026-10-13 07:32:38] | TASK START  2026-10-13-stream-verify.md (92 chars)
- [2026-10-13 07:32:41] | TASK LLM OK  2026-10-13-stream-verify.md | model=ep-20261013070524-xjjn2 tokens=?
- [2026-10-13 07:32:41] | TASK DONE    2026-10-13-stream-verify.md -> done/2026-10-13-stream-verify.md.result.md
- [2026-10-13 07:43:50] | TASK START  2026-10-13-onboarding-recall.md (251 chars)
- [2026-10-13 07:44:09] | TASK LLM OK  2026-10-13-onboarding-recall.md | model=ep-20261013070524-xjjn2 tokens=?
- [2026-10-13 07:44:09] | TASK DONE    2026-10-13-onboarding-recall.md -> done/2026-10-13-onboarding-recall.md.result.md
- [2026-10-13 08:12:06] | AUTO SPAWN auto-20261013-0812-Tectonic-final_density-语义取证-输入-输出语义-取值范围.md
- [2026-10-13 08:12:06] | TASK START  auto-20261013-0812-Tectonic-final_density-语义取证-输入-输出语义-取值范围.md (497 chars)
- [2026-10-13 08:12:11] | TASK LLM OK  auto-20261013-0812-Tectonic-final_density-语义取证-输入-输出语义-取值范围.md | model=ep-20261013070524-xjjn2 tokens=?
- [2026-10-13 08:12:11] | TASK DONE    auto-20261013-0812-Tectonic-final_density-语义取证-输入-输出语义-取值范围.md -> done/auto-20261013-0812-Tectonic-final_density-语义取证-输入-输出语义-取值范围.md.result.md
- [2026-10-13 08:12:11] | AUTO SPAWN auto-20261013-0812-Tectonic-final_density-语义取证-输入-输出语义-取值范围.md
- [2026-10-13 08:12:11] | TASK START  auto-20261013-0812-Tectonic-final_density-语义取证-输入-输出语义-取值范围.md (497 chars)
- [2026-10-13 08:12:16] | TASK LLM OK  auto-20261013-0812-Tectonic-final_density-语义取证-输入-输出语义-取值范围.md | model=ep-20261013070524-xjjn2 tokens=?
- [2026-10-13 08:12:16] | TASK DONE    auto-20261013-0812-Tectonic-final_density-语义取证-输入-输出语义-取值范围.md -> done/auto-20261013-0812-Tectonic-final_density-语义取证-输入-输出语义-取值范围.md.result.md
- [2026-10-13 08:12:16] | AUTO SPAWN auto-20261013-0812-Tectonic-final_density-语义取证-输入-输出语义-取值范围.md
- [2026-10-13 08:12:16] | TASK START  auto-20261013-0812-Tectonic-final_density-语义取证-输入-输出语义-取值范围.md (497 chars)
- [2026-10-13 08:12:19] | TASK LLM OK  auto-20261013-0812-Tectonic-final_density-语义取证-输入-输出语义-取值范围.md | model=ep-20261013070524-xjjn2 tokens=?
- [2026-10-13 08:12:19] | TASK DONE    auto-20261013-0812-Tectonic-final_density-语义取证-输入-输出语义-取值范围.md -> done/auto-20261013-0812-Tectonic-final_density-语义取证-输入-输出语义-取值范围.md.result.md
- [2026-10-13 08:12:19] | AUTO SPAWN auto-20261013-0812-Tectonic-final_density-语义取证-输入-输出语义-取值范围.md
- [2026-10-13 08:12:19] | TASK START  auto-20261013-0812-Tectonic-final_density-语义取证-输入-输出语义-取值范围.md (497 chars)
- [2026-10-13 08:12:25] | TASK LLM OK  auto-20261013-0812-Tectonic-final_density-语义取证-输入-输出语义-取值范围.md | model=ep-20261013070524-xjjn2 tokens=?
- [2026-10-13 08:12:25] | TASK DONE    auto-20261013-0812-Tectonic-final_density-语义取证-输入-输出语义-取值范围.md -> done/auto-20261013-0812-Tectonic-final_density-语义取证-输入-输出语义-取值范围.md.result.md
- [2026-10-13 08:12:25] | AUTO SPAWN auto-20261013-0812-Tectonic-final_density-语义取证-输入-输出语义-取值范围.md
- [2026-10-13 08:12:25] | TASK START  auto-20261013-0812-Tectonic-final_density-语义取证-输入-输出语义-取值范围.md (497 chars)
- [2026-10-13 08:12:31] | TASK LLM OK  auto-20261013-0812-Tectonic-final_density-语义取证-输入-输出语义-取值范围.md | model=ep-20261013070524-xjjn2 tokens=?
- [2026-10-13 08:12:31] | TASK DONE    auto-20261013-0812-Tectonic-final_density-语义取证-输入-输出语义-取值范围.md -> done/auto-20261013-0812-Tectonic-final_density-语义取证-输入-输出语义-取值范围.md.result.md
- [2026-10-13 08:12:31] | AUTO SPAWN auto-20261013-0812-Tectonic-final_density-语义取证-输入-输出语义-取值范围.md
- [2026-10-13 08:12:31] | TASK START  auto-20261013-0812-Tectonic-final_density-语义取证-输入-输出语义-取值范围.md (497 chars)
- [2026-10-13 08:12:36] | TASK LLM OK  auto-20261013-0812-Tectonic-final_density-语义取证-输入-输出语义-取值范围.md | model=ep-20261013070524-xjjn2 tokens=?
- [2026-10-13 08:12:36] | TASK DONE    auto-20261013-0812-Tectonic-final_density-语义取证-输入-输出语义-取值范围.md -> done/auto-20261013-0812-Tectonic-final_density-语义取证-输入-输出语义-取值范围.md.result.md
- [2026-10-13 08:12:36] | AUTO SPAWN auto-20261013-0812-Tectonic-final_density-语义取证-输入-输出语义-取值范围.md
- [2026-10-13 08:12:36] | TASK START  auto-20261013-0812-Tectonic-final_density-语义取证-输入-输出语义-取值范围.md (497 chars)
- [2026-10-13 08:12:40] | TASK LLM OK  auto-20261013-0812-Tectonic-final_density-语义取证-输入-输出语义-取值范围.md | model=ep-20261013070524-xjjn2 tokens=?
- [2026-10-13 08:12:40] | TASK DONE    auto-20261013-0812-Tectonic-final_density-语义取证-输入-输出语义-取值范围.md -> done/auto-20261013-0812-Tectonic-final_density-语义取证-输入-输出语义-取值范围.md.result.md
- [2026-10-13 08:12:40] | AUTO SPAWN auto-20261013-0812-Tectonic-final_density-语义取证-输入-输出语义-取值范围.md
- [2026-10-13 08:12:40] | TASK START  auto-20261013-0812-Tectonic-final_density-语义取证-输入-输出语义-取值范围.md (497 chars)
- [2026-10-13 08:12:43] | TASK LLM OK  auto-20261013-0812-Tectonic-final_density-语义取证-输入-输出语义-取值范围.md | model=ep-20261013070524-xjjn2 tokens=?
- [2026-10-13 08:12:43] | TASK DONE    auto-20261013-0812-Tectonic-final_density-语义取证-输入-输出语义-取值范围.md -> done/auto-20261013-0812-Tectonic-final_density-语义取证-输入-输出语义-取值范围.md.result.md
- [2026-10-13 08:12:43] | AUTO SPAWN auto-20261013-0812-Tectonic-final_density-语义取证-输入-输出语义-取值范围.md
- [2026-10-13 08:12:43] | TASK START  auto-20261013-0812-Tectonic-final_density-语义取证-输入-输出语义-取值范围.md (497 chars)
- [2026-10-13 08:12:48] | TASK LLM OK  auto-20261013-0812-Tectonic-final_density-语义取证-输入-输出语义-取值范围.md | model=ep-20261013070524-xjjn2 tokens=?
- [2026-10-13 08:12:48] | TASK DONE    auto-20261013-0812-Tectonic-final_density-语义取证-输入-输出语义-取值范围.md -> done/auto-20261013-0812-Tectonic-final_density-语义取证-输入-输出语义-取值范围.md.result.md
- [2026-10-13 08:12:48] | AUTO SPAWN auto-20261013-0812-Tectonic-final_density-语义取证-输入-输出语义-取值范围.md
- [2026-10-13 08:12:48] | TASK START  auto-20261013-0812-Tectonic-final_density-语义取证-输入-输出语义-取值范围.md (497 chars)
- [2026-10-13 08:12:53] | TASK LLM OK  auto-20261013-0812-Tectonic-final_density-语义取证-输入-输出语义-取值范围.md | model=ep-20261013070524-xjjn2 tokens=?
- [2026-10-13 08:12:53] | TASK DONE    auto-20261013-0812-Tectonic-final_density-语义取证-输入-输出语义-取值范围.md -> done/auto-20261013-0812-Tectonic-final_density-语义取证-输入-输出语义-取值范围.md.result.md
- [2026-10-13 08:12:53] | AUTO SPAWN auto-20261013-0812-Tectonic-final_density-语义取证-输入-输出语义-取值范围.md
- [2026-10-13 08:12:53] | TASK START  auto-20261013-0812-Tectonic-final_density-语义取证-输入-输出语义-取值范围.md (497 chars)
- [2026-10-13 08:12:57] | TASK LLM OK  auto-20261013-0812-Tectonic-final_density-语义取证-输入-输出语义-取值范围.md | model=ep-20261013070524-xjjn2 tokens=?
- [2026-10-13 08:12:57] | TASK DONE    auto-20261013-0812-Tectonic-final_density-语义取证-输入-输出语义-取值范围.md -> done/auto-20261013-0812-Tectonic-final_density-语义取证-输入-输出语义-取值范围.md.result.md
- [2026-10-13 08:12:57] | AUTO SPAWN auto-20261013-0812-Tectonic-final_density-语义取证-输入-输出语义-取值范围.md
- [2026-10-13 08:12:57] | TASK START  auto-20261013-0812-Tectonic-final_density-语义取证-输入-输出语义-取值范围.md (497 chars)
- [2026-10-13 08:13:04] | TASK LLM OK  auto-20261013-0812-Tectonic-final_density-语义取证-输入-输出语义-取值范围.md | model=ep-20261013070524-xjjn2 tokens=?
- [2026-10-13 08:13:04] | TASK DONE    auto-20261013-0812-Tectonic-final_density-语义取证-输入-输出语义-取值范围.md -> done/auto-20261013-0812-Tectonic-final_density-语义取证-输入-输出语义-取值范围.md.result.md
- [2026-10-13 09:33:04] | TASK START  2026-10-13-dlc-v37.md (1512 chars)
- [2026-10-13 09:33:26] | TASK LLM OK  2026-10-13-dlc-v37.md | model=ep-20261013070524-xjjn2 tokens=?
- [2026-10-13 09:33:26] | TASK DONE    2026-10-13-dlc-v37.md -> done/2026-10-13-dlc-v37.md.result.md
- [2026-10-13 09:36:26] | TASK START  2026-10-13-github-mail.md (1096 chars)
- [2026-10-13 09:37:23] | TASK LLM OK  2026-10-13-github-mail.md | model=ep-20261013070524-xjjn2 tokens=?
- [2026-10-13 09:37:23] | TASK DONE    2026-10-13-github-mail.md -> done/2026-10-13-github-mail.md.result.md
- [2026-10-13 10:10:55] | AUTO SPAWN auto-20261013-1010-Tectonic-final_density-语义取证-输入-输出语义-取值范围.md
- [2026-10-13 10:10:55] | TASK START  auto-20261013-1010-Tectonic-final_density-语义取证-输入-输出语义-取值范围.md (497 chars)
- [2026-10-13 10:11:02] | TASK LLM OK  auto-20261013-1010-Tectonic-final_density-语义取证-输入-输出语义-取值范围.md | model=ep-20261013070524-xjjn2 tokens=?
- [2026-10-13 10:11:02] | TASK DONE    auto-20261013-1010-Tectonic-final_density-语义取证-输入-输出语义-取值范围.md -> done/auto-20261013-1010-Tectonic-final_density-语义取证-输入-输出语义-取值范围.md.result.md
- [2026-10-13 10:11:02] | AUTO SPAWN auto-20261013-1011-Tectonic-final_density-语义取证-输入-输出语义-取值范围.md
- [2026-10-13 10:11:02] | TASK START  auto-20261013-1011-Tectonic-final_density-语义取证-输入-输出语义-取值范围.md (497 chars)
- [2026-10-13 10:11:06] | TASK LLM OK  auto-20261013-1011-Tectonic-final_density-语义取证-输入-输出语义-取值范围.md | model=ep-20261013070524-xjjn2 tokens=?
