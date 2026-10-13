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
- [ ] 本地仓库 push 到 GitHub（代码+白板同步）
- [ ] v3.7 部署（patch_v37.py 落盘未推；剩 STALL守卫/清理循环/提案通道 3 件）
- [ ] 服务器 2026-11-12 续费
- [ ] ufw 出站白名单批准
- [ ] ARK Key 季度轮换

## 各方声明
- WorkBuddy：只读镜像 GitHub，不越权写；动手前读白板占锁
- 豆包-worker：git pull 读中枢，看锁/维护牌只读，部署先登记
- 本地豆包：唯一写者（用户定），写前读中枢
