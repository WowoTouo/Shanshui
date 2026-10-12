# 部署报告 · md 格式铁律落地（2026-10-13 05:44-05:49）

## 指令

1. 「以后每一次发邮箱都使用 md 文件」
2. 范围扩大：「包括生成的报告日志这些都尽可能用 md 格式」

## 改动清单（3 个文件，本地与服务器 md5 一致）

| 文件 | 版本 | md5 | 改动 |
|---|---|---|---|
| `summary.sh` | v4 | `92511ef9…` | 邮件段重写为 multipart/mixed |
| `disk-alert.sh` | v2 | `fe51c914…` | 新增 md 告警报告 |
| `fw-sync.py` | v2 | 本地即时生效 | 同步日志转 md 格式 |

### 1. summary.sh v4 —— 邮件全 md 化

- 正文：`Content-Type: text/markdown; charset=UTF-8`，内容 = 当天日报 md 原文
- 附件：日报 `.md` 原件（base64，`filename=YYYY-MM-DD.md`）
- 结构：`multipart/mixed`，边界 `shanshui-<epoch>-<pid>`
- worker.log 记录行改为「mail(md) sent to …」

### 2. disk-alert.sh v2 —— 告警也有 md 报告

- 触发时生成 `/home/agent/logs/alerts/YYYY-MM.md`
- 结构：`## 时间 磁盘使用率 N%` 标题 + 阈值 / 分区现状 / agent 目录占用 / 处置建议 bullet 列表

### 3. fw-sync.py v2 —— 本地同步日志转 md

- `logs/fw-sync.log`（纯文本，留存作历史）→ `logs/fw-sync.md`（md bullet 格式，首建自动写说明头）
- 已 grep 证实无任何脚本消费该日志，转换零风险

## 验证记录

| 验证项 | 方法 | 结果 |
|---|---|---|
| 语法 | `bash -n` ×2 + `py_compile` | 全过 |
| MIME 结构 | 本地干跑 + Python email 解析器 | 边界完整、2 个 leaf part、正文与附件和日报 md **字节级一致** |
| 告警分支 | `THRESHOLD=1` 强制触发干跑 | md 报告结构正确 |
| fw-sync | 实跑一轮 | md 日志正常；出口 v4=120.40.85.228 / v6=240e:379:283:b600，白名单已有，无需变动 |
| 端到端 | 服务器 `sudo -u agent summary.sh` | exit=0；`mail(md) sent to chn_wwt@outlook.com WouoTouo@foxmail.com`；msmtp `250 OK: queued`（mailsize 958） |

> 端到端测试已真实发信——两个收件箱（outlook + foxmail）各收到一封带 `.md` 附件的 md 日报，可直接查收确认格式。

## 分层原则（「尽可能」的工程裁量）

- **用户可见产物全 md**：日报 `.md` ✓、邮件（正文 markdown + md 附件）✓、告警报告 `.md` ✓、任务结果 `done/*.md` ✓
- **机器流水日志保持纯文本**：`worker.log` 是 summary.sh 的 grep 数据源，其 md 渲染层就是日报本身
- 明早 06:00 cron 起，每日自动推送 md 日报邮件到两个收件箱

## 仍阻塞（不变）

三把钥匙：方舟 API Key + endpoint id ×2（lite/pro）+ GitHub 仓库地址 → 填 `/home/agent/.env` → 重启 ai-worker → first-task 端到端闭环 → 船长 review。
