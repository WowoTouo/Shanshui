# Shanshui 全局协调状态（STATE）

- 最后更新：2026-10-13 16:40 CST
- 维护者：豆包（Make 角色，唯一同步桥）
- 唯一事实源：本文件（GitHub 仓库 `coordination/STATE.md`）；云端镜像由豆包单向同步至 WorkBuddy 空间

## 一、三方分工（已确认，2026-10-13）

| 角色 | 主体 | 职责 | 活跃度 |
| --- | --- | --- | --- |
| 总工 | 用户 | 定方向 / 验收 / 批权限 / 模型选型 | — |
| Make | 豆包（本地客户端） | SSH 运维、部署、GitHub 读写（唯一写者）、巡检、收 ai-worker 记忆 | 活跃 |
| Archive | WorkBuddy | 云端归档 / 记忆存储 / 只读镜像（不写活源、不 ssh、不改配置） | 存储层 |
| Run | 服务器 ai-worker | 从 GitHub 拉取任务运行、写 logs/ + memory/daily/ | 单实例运行 |

## 二、防冲突协议（三方共同遵守）

1. **GitHub = 唯一活源**；本 STATE.md = 唯一状态真相。任何一方动手前先读 STATE.md。
2. **豆包 = 唯一写者**：push 前先 pull 对齐；冲突在 git 里可追溯、可回滚。
3. **WorkBuddy = 只读镜像**：只收豆包同步过去的归档快照（.md），不写活源、不改配置。
4. **ai-worker = 不直接改 GitHub**：任务结果/记忆经豆包回写沉淀。
5. 任何异常：先看 STATE.md + git log + `/home/agent/logs/worker.log`，再归因。

## 三、各方意见（2026-10-13 记录）

- **豆包（Make）意见**：以 GitHub 的 STATE.md 为唯一状态中枢，豆包做同步桥——所有变更先落 STATE.md 再行动，三方读同一状态，杜绝隐式假设。
- **WorkBuddy（Archive）应遵守的约定**：只读云端镜像文件夹；发现镜像更新不自行改源，仅在归档区记录；涉及活源变更一律通过豆包转达总工，不越权写入。

## 四、当前统一进度

- [进行] v3.7 剩余 3 防身件：STALL 守卫 / 清理循环 / 提案通道（豆包执行中，改完即 push）
- [进行] WorkBuddy 模型切换：Step-5 → 混元三（总工在界面操作，豆包侧无动作）
- [待办] 服务器续费 2026-11-12 到期
- [待办] cron 布局理顺（`/home/agent/worker/` vs `/home/agent/work/tools/` 两处并存）
- [待办] 服务器 ufw 出站白名单 / ARK Key 季度轮换

## 五、变更日志

- 2026-10-13 16:40 建立共享状态文件；三方分工确认（总工/Make/Archive/Run）；各方意见记录
- 2026-10-13 16:23 服务器 v3.7 四层注入上线（PROMPT+ONBOARDING+AUTONOMY+DLC-001，15120 chars）
- 2026-10-13 v3.6.1 部署完成；文件体系规范（.cloud/worker 分层）；GitHub 打通（PAT 凭证库）
- 2026-10-13 云化 42 文件至 WorkBuddy 空间（HoOX0pG4vumjS23Bhzja3C）
