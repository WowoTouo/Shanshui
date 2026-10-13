# OPS-STATE.md — 山水协作锁板（基石 §五 落地）

- 最后更新：2026-10-13 17:2x CST
- 维护：科学/发展/山水 三方共写；**本文件即权威主文件（服务器 `/home/agent/OPS-STATE.md`）**；GitHub `coordination/OPS-STATE.md` 为备用镜像
- 协议：`claim（占锁）→ 执行 → release（放锁）`；锁未过期（默认 30 分钟）→ 只读围观

## 当前锁状态

- 持有方：`无`
- 锁过期：`无`
- 当前动作：`无（v3.7 三件套已装完 release）`
- 装完 release；发展只读围观不抢锁

## 运行基准

- 服务：ai-worker.service（active）
- worker.py 版本：v3.7 四层注入（PROMPT+ONBOARDING+AUTONOMY+dlc/DLC-001）
- worker.py md5：`待更新（claim 时刷新）`
- 日志：/home/agent/logs/worker.log

## 维护牌 / 待交接

- 无维护牌
- 待交接：v3.7 三件套（STALL/清理/提案）→ cron 理顺 → 续费 2026-11-12 → ufw/Key 轮换

## 最近动作（留痕）

| TS | 动作方 | 动作 | 结果 |
| --- | --- | --- | --- |
| 2026-10-13 16:23 | 科学 | 部署 v3.7 四层注入 | 成功（15120 chars 生效） |
| 2026-10-13 15:58 | 科学 | 部署 v3.6.1 | 成功（自检 TASK DONE） |
| 2026-10-13 | 科学 | 云化 42 文件至 WorkBuddy | 成功 |
| 2026-10-13 17:10 | 发展 | 填 FOUNDATION §四（接任） | 成功（claim→release 留痕） |
| 2026-10-13 17:3x | 科学 | 重置自主配额（删 count 12→0） | 成功（恢复山水自主派发） |
| 2026-10-13 17:3x | 科学 | 三地核验 worker.py md5（21121b96/26279B = v3.7 四层注入） | 一致，无漂移 |
| 2026-10-13 17:2x | 科学 | 装 v3.7 三件套（STALL守卫/清理循环/提案通道） | 成功：单测全绿+服务器重启日志确认（CLEANUP 触发） |
