# 任务：链接 GitHub + 邮件报告验证
优先级：高

## 背景
总工已完成 v3.7 素材落位（PROMPT.md / DLC-001 / cleanup.sh / daily-card.sh / send-result-mail.sh / 交接单 已在 /home/agent/ 下）。本任务把服务器仓库连上 GitHub、验证邮件通道。

## 一、GitHub 链接（origin 从本地 bundle 切到远程）
1. cd /home/agent/Shanshui
2. git remote remove origin（若 origin 指向 /tmp/shanshui-server.bundle）
3. git remote add origin https://github.com/WowoTouo/Shanshui.git
4. git fetch origin && git pull origin main（公开仓库匿名可拉）
5. 验证：git log --oneline -1 与远程一致（远程头约 1cbc7d4 或更新）
6. 推送纪律（如要 push）：ONBOARDING.md §4A 三道护栏——只 add memory/、.cloud/worker/、docs/、learnings/；commit 带 [ai] 前缀；禁动 src/、build.gradle；push 用 clean URL + .env 的 GITHUB_TOKEN

## 二、邮件报告验证
1. /home/agent/work/tools/send-result-mail.sh 已部署（755）——测试发送一封：标题「[测试] 服务器邮件通道验证」
2. 验证：脚本 exit 0 + 收件箱收到（收件人 = .env 的 MAIL_TO/MAIL_TO2）
3. 汇报：发送时间、收件人、脚本输出摘要

## 三、纪律（强制）
1. **所有命令必须写在 bash 代码块中**（```bash 开头）——当前 worker v3.6 只执行 bash 块；方舟模型发的 tool_call XML 不执行（v3.7 会修复，本任务先守 bash 块纪律）
2. 完成后把结果写进本任务 result（结论置顶 ≤3 句 + 证据路径）

## 四、验收
- git remote -v 显示 github.com/WowoTouo/Shanshui
- git log 与远程对齐
- 测试邮件已发送且收到
- 汇报：git 对齐结果 + 邮件发送结果
