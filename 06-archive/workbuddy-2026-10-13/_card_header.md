# 妙计：山水自主修复 v3.7 双 bug（空结果 + STALL 卡死）
> 签发：总工 → 执行：山水（worker 自主）｜优先级：高｜授权：总工本次**例外**授权修改自身 worker.py（v3.7.2 补丁）

你是山水 worker。总工授权你本次**例外**修改自己的 worker.py，修复两个已实锤的 bug。补丁由「发展」写好并实测通过（幂等 + 锚点校验 + 备份 + 编译闸），你只需原样打上并验证。**铁律：任何一步输出异常就立即停止、在 result 写明；绝不重启服务；绝不 git commit/push。**

## 背景（已取证，勿再调查）
- **bug1 空结果**：Doubao-Seed-Evolving 把整段回复塞进 `<seed:think_xxx>...</think_xxx>` 思考块，`strip_think_tags()` 剥光 → result 只剩完成头（19:56 / 20:13 两张自检卡实锤，均 `tokens=?`）。
- **bug2 STALL 卡死**：`spawn_auto_task()` 目标状态行不变就 `return None`；上游空结果 → AI 没更新 backlog 状态行 → sig 永不变 → 自主派发每 60s 跳过、永久冻结（今日已 64 次）。
- **根因关联**：bug1 是因，bug2 是果（没产出 → 没更新状态行 → STALL 永不放行）。

## 步骤 1／4：创建补丁脚本（内容由发展提供，原样落盘，勿改）
```bash
cat > /home/agent/work/patch_v372.py <<'PYEOF'
