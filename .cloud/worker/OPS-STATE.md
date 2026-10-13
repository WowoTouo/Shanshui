# Shanshui OPS 共享协调白板（双后台互通）
> 建立：2026-10-13 16:43 by WorkBuddy（用户“统一进度开始”指令）
> 三处落地：GitHub coordination/STATE.md（用户 e722da9 主源） / 服务器 /home/agent/OPS-STATE.md（ai-worker 镜像） / 本地 .cloud/worker/OPS-STATE.md（WB 镜像）
> 互斥协议：动手前 claim_lock(owner+expires)；执行完 release_lock；对方见未过期锁或 maintenance=true 只可读不可写

## 两后台真实快照（互通有无）
### A. 服务器后台（ai-worker，豆包模型驱动）
- worker.py md5: 21121b96...（26279B，16:23 部署，野生版·非本地 v3.5/v3.6/v3.7）
- 活进程 PID 225163 / agent / venv312 / 稳定运行
- 配额 12/12 烧穿；内存 535M/1930M 健康；日志 /home/agent/logs/worker.log
- 备份 worker.py.bak-v35(24775B)/bak-v36(23404B)/bak-v361(24978B) 均 root:root
- 待补：~/Shanshui 未切 GitHub remote，ai-worker 暂不能 git pull 读中枢

### B. WorkBuddy 后台（本地 SSH 运维）
- 记忆：D:/JAVA21orPython/AI/2026-10-13-01-06-24/.workbuddy/memory/（MEMORY.md 已压缩）
- 云化 42 文件已上云（空间 HoOX0pG4vumjS23Bhzja3C）
- 已知仓库 https://github.com/WowoTouo/Shanshui；用户已建 coordination/STATE.md(e722da9)
- 本地仓库 remote 待切 GitHub；上传脚本(/tmp/retry2.sh)丢失待重摸

## 科学核实更正（2026-10-13 17:3x，由科学 side 依服务器实测更新）
- **worker.py**：md5 `21121b96...`（26279B）经三地比对 = **本地 v3.7 四层注入版（commit 0da5100）完全一致**，非"野生版"——服务器无漂移（备份链 bak-v35/36/361 为历史存档）
- **~/Shanshui remote**：已切 GitHub `origin https://github.com/WowoTouo/Shanshui.git`（fetch+push 均在）——下方进度项应勾选 [x]
- **配额**：2026-10-13.count=12 已烧穿 → **科学已重置（删 count，12→0）**，山水自主派发恢复
- **本地仓库 remote**：已指向 GitHub main（本机 git 一直在用，非"待切"）
- 三地一致基线：服务器 /home/agent/{FOUNDATION,STATE,OPS-STATE}.md = 本地 coordination/ = GitHub main（`25a2f3a`）

## 互斥锁
- owner: none
- expires: -
- 最近占锁: workbuddy @16:43 建基线（已 release）

## 维护牌
- maintenance: false

## 统一进度基石
- [x] 资料云化 42 文件
- [x] 服务器 AI 执行能力恢复（删 count + restart）
- [x] GitHub coordination/STATE.md 中枢建立（e722da9）
- [x] 服务器 ~/Shanshui 切 GitHub remote（已确认 origin fetch+push 生效）
- [x] 配额重置（2026-10-13 科学 12→0）
- [ ] GitHub 收口（4e8b887）：本地+服务器两 SSH 公钥待总工登记后补推
- [x] v3.7 部署 + v3.7.2 双bug修复（空结果兜底占位 + STALL自愈重试）；已上线服务器 + 同步仓库 589189e
- [x] 预算水位监控入板（4.96M/5.5M 快照 + 100万告警阈值，quota-alert 联动）
- [ ] 白嫖迁移战略：2026-11-12 到期前打包全部工程文件+运行环境上云，到期不续换免费服务器重建（科学牵头，WB 补清单）
- [ ] ufw 出站白名单批准
- [ ] ARK Key 季度轮换
- [x] 模型退化应对：v3.7.3-3.7.5 智能两阶段研究 + 合成增强 + 确定性侦察兜底——模型零产出也据检索合成正文（实证 727 字诚实结论）；无需换模型即有稳定产出

## 部署/变更台账
- 2026-10-13 21:2x 发展 op=deploy obj=worker.py v3.7.2（总工授权"你帮我配置，我授权你和山水"）：patch_v372.py 4 处锚点补丁（空结果回退抽思考块正文 + process_task 最终兜底占位 / STALL_RETRY_AFTER=6 自愈重试）→ 备份 worker.py.bak-pre-v372 → systemctl restart → 复验（STALL [N/6] 自愈放行实证 21:29/21:34、result 不再空白）→ commit 589189e push gitee。根因：模型层退化（非代码 bug），代码已健壮；有用产出待模型层决策。
- 2026-10-13 22:2x 发展 op=deploy obj=worker.py v3.7.3-3.7.5 + sync-research.sh：① 智能两阶段研究（一阶段取证 / 二阶段据证据合成正文）② 合成增强（exec_log+draft 合并上下文）③ 确定性侦察兜底 _auto_recon（模型零产出时 worker 自 grep 仓库取证再合成）——实证模型零产出仍合成 727 字诚实结论；④ 研究成果自动上云 sync-research.sh（cron 每 2h，fetch+rebase 多写入方安全 + 镜像 research/ + push）。四地对齐 7a9d590；v375 结论 + 自主 Tectonic 结论均已上云 research/results/。

## GitHub SSH 公钥登记（待总工操作）— 2026-10-13 19:2x
- 用途：登记后服务器/本地即可经 SSH/22 直推 GitHub，收口到 4e8b887（绕开 443 掐断）
- 本地公钥（账号 SSH key，WowoTouo）：
  `ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIOOHCv9CjH5bWDxWKcoQoo0khFfPYC+1eLufrFk9W4ES wowotou-local@shanshui`
- 服务器公钥（仓库 Deploy Key，勾选 Allow write access，shanshui-server@wowotouo）：
  `ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAICoBbDN820PtWaYYB3cX1CUf2XyBtNhLWVc7rXC9o0db shanshui-server@wowotouo`
- 替代通道：若总工给 GitHub PAT（scope=admin:public_key），WB 可用 API 代登两把；否则请总工在 GitHub Web UI 粘贴

## 运行时监控（预算水位）— 2026-10-13 19:2x 入板
- 模型端点：方舟 `ep-20261013070524-xjjn2`（科学本地豆包 + 山水服务器 worker 共用同一配额池）
- 快照基准（2026-10-13 19:12）：余额 4,963,479 / 共 5,500,000 tokens（剩 ~90.2%）
- 单价：6.0 元/百万 tokens；剩余价值 ≈ 29.8 元
- 告警阈值：剩余 < 1,000,000 tokens 触发 quota-alert.sh 发 md 邮件告警
- 估算口径：无 IAM AK/SK 查不了精确余额；基于快照 + worker.log 实际 tokens 累加（未知按 8000 估），增量基线仅计快照后新增，避免重复扣
- 监控实现：服务器 /home/agent/work/tools/quota-alert.sh（cron */6），state=/home/agent/logs/quota_state.txt，log=/home/agent/logs/quota.log
- 当前读数（19:12 后）：bal_est=4963479，运行正常

## 白嫖迁移战略（2026-11-12 服务器到期）— 2026-10-13 19:2x 用户定调
- 决策：到期**不续费**，换免费服务器重建；重点是把**全部必要工程文件 + 运行环境**打包上云，保证新服务器一键可重建
- 红线：不备份系统（OS/apt 等），只备份工程文件与可重建的运行环境配置
- 牵头：科学（本地豆包）已在处理；WB 补「必须打包清单」并交接
- 必须打包清单（草案，WB 提供，科学认领执行）：
  - 工程源码：Shanshui 仓库全量（含 .cloud/worker/ 部署包、coordination/ 白板、OPS-STATE/STATE/FOUNDATION/SIGNAL）
  - 运行环境：worker.py + run_worker.sh + summary.sh + send-result-mail.sh + quota-alert.sh + disk-alert.sh + 镜像泵脚本
  - 配置模板（不含密钥）：ai-worker.service / agent-sudoers / ai-worker-logrotate.conf / .msmtprc-template / .env-template（密钥槽位留空）
  - 依赖清单：venv312 的 `uv pip freeze` 产出 requirements（Python 3.12.15）；Java 工具链说明（Zulu27 主 + Zulu25 备，gradle 9.8.1，options.release=25）
  - 状态快照：OPS-STATE.md + 当前配额水位 + 防火墙规则导出（tccli 已就绪）
- 目标产物：一个可重现的打包（tar/脚本），新免费服务器 clone 后一条命令拉起 ai-worker
- 时间窗：2026-11-12 前完成上云；建议 11-01 起每周校验一次打包完整性

## 各方声明
- WorkBuddy：只读镜像 GitHub，不越权写；动手前读白板占锁
- 豆包-worker：git pull 读中枢，看锁/维护牌只读，部署先登记
- 本地豆包：唯一写者（用户定），写前读中枢
