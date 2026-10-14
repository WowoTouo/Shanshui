# REBUILD.md — 山水 AI Worker 重建手册（白嫖迁移版）

> 目标：新免费服务器（Ubuntu x86_64，1-2G 内存即可）从零重建 7×24 自主 AI worker
> 全程约 30 分钟；worker.py 零第三方 pip 依赖（纯标准库 + curl），迁移极轻
> 前置：git clone 本仓库 + 拿到 `.env` 加密包（密码见本地 README-SECRET.txt，不进 git）

## 0. 材料清单
| 材料 | 位置 | 说明 |
|---|---|---|
| 代码+指南+工具 | 本仓库（`.cloud/worker/`） | Gitee 主 / GitHub 备用 |
| 敏感配置 | `.env` 加密包（zip -P） | ARK key / 邮箱密码 / token，**永不进 git** |
| 服务器 | Ubuntu 22.04+ x86_64 | root 或 sudo |

## 1. 基础环境
```bash
sudo apt update && sudo apt install -y git curl msmtp msmtp-mta cron unzip
# Python：用 uv 装 3.12.15 建 venv312（纪律：别装系统 python）
# worker 纯标准库，但统一 3.12.15 规避 Ubuntu 26.04 系统 3.14 的不确定性
curl -LsSf https://astral.sh/uv/install.sh | sh
sudo -u agent bash -c 'cd /home/agent && uv venv --python 3.12.15 venv312'
```

## 2. 建 agent 用户 + 目录
```bash
sudo useradd -m -s /bin/bash agent
sudo mkdir -p /home/agent/{worker,work/tools,logs,tasks,done,memory,proposals,dlc,bin}
sudo chown -R agent:agent /home/agent
```

## 3. 拉代码
```bash
cd /home/agent
sudo -u agent git clone https://gitee.com/zhong-li-of/Shanshui.git Shanshui
# 备用：https://github.com/WowoTouo/Shanshui.git
```

## 4. 部署映射（仓库 → `/home/agent/`）
> ⚠️ 脚本分两处、勿混：cron 按绝对路径调，放错位置即断 job
| 源（仓库内） | 目标 | 说明 |
|---|---|---|
| `worker.py` `run_worker.sh` `summary.sh` `disk-alert.sh` `test_worker_local.py` | `/home/agent/worker/` | 主程序+常驻脚本（cron 06:00 summary / */6 disk 在此调）|
| `tools/chronicle.sh` `tools/cleanup.sh` `tools/daily-card.sh` `tools/gitee-github-bridge.sh` `tools/quota-alert.sh` `tools/send-result-mail.sh` `tools/verify-build.sh` | `/home/agent/work/tools/`（chmod 755）| 辅助工具（bridge/quota/chronicle cron 在此调）|
| `PROMPT.md` `ONBOARDING.md` `AUTONOMY.md` `DLCOPS.md` | `/home/agent/` | 四层注入指南 |
| `dlc/DLC-001-daily-operations.md` `dlc/DLC-002-external-integration.md` `dlc/DLC-003-autonomous-self-iteration.md` `dlc/DLC-004-auto-research-pipeline.md` | `/home/agent/dlc/` | DLC 扩展层（四张卡） |
| `tools/push-wecom.py` `tools/preflight-check.sh` `tools/gen-runbook.sh` | `/home/agent/work/tools/`（chmod 755）| 企微推送 / 启动前对比 / 运行指南生成 |
| `conf/ai-worker.service` | `/etc/systemd/system/` | systemd 服务（含 CPUQuota=80%）|
| `conf/agent-sudoers` | `/etc/sudoers.d/agent-worker`（visudo -c 校验后 0440）| worker 免密 sudo 白名单 |
| `conf/ai-worker-logrotate.conf` | `/etc/logrotate.d/ai-worker` | 日志轮转 |
| `conf/msmtprc-template` | `/home/agent/.msmtprc`（改邮箱，600）| 邮件通道 |
| `coordination/FOUNDATION.md STATE.md OPS-STATE.md SIGNAL.md CHRONICLE.md MODEL-REGISTRY.md` | `/home/agent/`（agent 644，可选）| 协调/档案/模型记忆，接旧状态才恢复 |
> 注：`fw-sync.py` `weekly-snapshot.py` 是**客户端（你的 Windows PC）**脚本，不部署到服务器；迁移时单独带走并改指向新服务器 IP（见 §13）。

## 5. 配置 .env（从加密包恢复，600 权限）
```bash
sudo -u agent install -m 600 <解密后.env> /home/agent/.env
# 键：ARK_API_KEY / ARK_BASE_URL / ARK_MODEL_LITE / ARK_MODEL_PRO /
#     AUTONOMY_BUDGET / MAIL_FROM / MAIL_PASS / MAIL_TO / FEISHU_WEBHOOK / GITHUB_TOKEN /
#     JAVA_HOME=/usr/lib/jvm/zulu27 / JAVA_HOME_ALT=/usr/lib/jvm/zulu25（mod 构建用；worker 不依赖）
```

## 6. 装服务 + 启动
```bash
sudo systemctl daemon-reload
sudo systemctl enable --now ai-worker
# 日志：/home/agent/logs/worker.log
```

## 7. 单测
```bash
cd /home/agent/worker && python test_worker_local.py
# 期望：ALL LOCAL TESTS PASS
```

## 8. 验证四层注入（关键验收）
```bash
sudo tail -10 /home/agent/logs/worker.log
# 期望看到：
#   === worker process start (v3.7) ===
#   GUIDES loaded (...): PROMPT.md + ONBOARDING.md + AUTONOMY.md + dlc:DLC-001
#   CLEANUP: 每日清理检查已触发
```

## 9. 恢复 cron（agent 用户）
```bash
sudo -u agent crontab -l > /tmp/c; cat >> /tmp/c <<'EOF'
0 6 * * * /home/agent/worker/summary.sh
0 */6 * * * /home/agent/worker/disk-alert.sh
*/30 * * * * /usr/bin/flock -n /tmp/bridge.lock bash /home/agent/work/tools/gitee-github-bridge.sh
*/6 * * * * /usr/bin/flock -n /tmp/quota.lock bash /home/agent/work/tools/quota-alert.sh
0 7 * * * /usr/bin/flock -n /tmp/chr.lock bash /home/agent/work/tools/chronicle.sh
EOF
sudo -u agent crontab /tmp/c
```

## 10. 恢复双 remote + 凭证
```bash
# 凭证：.git-credentials（GitHub https + Gitee https 两行，600）
# origin=GitHub: https://github.com/WowoTouo/Shanshui.git
# gitee=https://gitee.com/zhong-li-of/Shanshui.git
bash /home/agent/work/tools/gitee-github-bridge.sh   # 手动跑一次验证
```

## 11. 协调文件（可选恢复旧状态）
`FOUNDATION.md / STATE.md / OPS-STATE.md / SIGNAL.md` → `/home/agent/`（agent 属主 644）
新环境可重新开始；要接旧记忆就从仓库 `coordination/` 恢复。

## 12. 验收清单（全绿 = 重建成功）
- [ ] worker 启动日志 v3.7 + 四层注入 + CLEANUP 触发
- [ ] 单测 ALL LOCAL TESTS PASS
- [ ] cron 5 条就位（summary/disk/bridge/quota/chronicle）
- [ ] Gitee/GitHub 双 remote push 通（bridge 手动跑 OK）
- [ ] 自主派发出任务卡（配额 budget 内）
- [ ] 邮件/飞书通知通道通（send-result-mail.sh 试发）

## 13. 范围与客户端适配（迁移勿漏）
- **本手册只重建 AI worker**（纯 Python，零三方依赖）。若要重建 Shanshui mod 本体，另需 Java 工具链：
  - Azul Zulu 源装 `zulu27-jdk`（主）+ `zulu25-jdk`（备）；Gradle 9.8.1 落 `/opt/gradle-9.8.1`
  - `.env` 已有 `JAVA_HOME=/usr/lib/jvm/zulu27` + `JAVA_HOME_ALT=/usr/lib/jvm/zulu25`
  - `build.gradle`：toolchain `of(27)` + `options.release=25`（产物 major 69 = Java 25 向下兼容）
- **客户端防火墙同步**：`fw-sync.py`（在你的 Windows PC 跑，非服务器）绑定了旧服务器 IP 111.230.231.174；换新服务器后必须改指向新 IP，并把新 IP 加进云厂商防火墙 22 白名单（家宽双通道出口 IP 也要在）。
- **仓库可见性**：§3 的 HTTPS clone 若仓库为私有会失败——要么把 Gitee 仓库设 public，要么把 `.git-credentials` 恢复提前到 clone 之前。
- **worker.py 备份链**：服务器有 bak-v35/36/361/37 四个，仓库只跟踪 bak-v36/37；如要完整历史，从服务器打包带走 bak-v35/bak-v361。

## 附：敏感资产清单（加密包内容）
`.env`（方舟 key + 邮箱 + token）、`.git-credentials`（GitHub/Gitee 凭证）
→ 打包 `zip -P <密码> secrets.zip .env .git-credentials`，密码存本地 README-SECRET.txt
