# worker v3.4 流式化改造 · 验收报告（2026-10-13）

## 一、改动内容（commit `fc6c3d1`）

| 文件 | 改动 |
|---|---|
| `.cloud/worker/worker.py` | 新增 `chat_completions_stream(client, model, messages)`：`create(stream=True)` 迭代聚合 chunk；**错误在迭代中途上抛不吞**，交主循环 try/except 走退避/熔断；usage 仅末 chunk 顶层捕获，缺失返回 None |
| 同上 | `process_task` 重写调用处：聚合全文 → `redact` → `strip_think_tags` → `tokens` 统计（顺序不变），日志 `tokens=?` 降级不报错 |
| `.cloud/worker/test_worker_local.py` | 新增 [8]/[8b]/[8c] 流式三分支：聚合拼接 + 末 chunk usage + `stream=True` 透传断言 / 无 usage 降级 None / 中途 RuntimeError 上抛断言（mock chunk，不触网） |
| `.cloud/worker/tasks/2026-10-13-stream-verify.md` | 流式实测任务（`model: lite`，50 字解释密度函数，只读） |

## 二、回归结果

- **本地单测 25 项全过**（22 项历史 + 流式三分支），含 404 回归 [6]、思考块防误执行 [7]
- **服务器 py_compile 通过**（venv312 / Python 3.12，跨 minor 版本校验）
- 服务器 `~/Shanshui` 仓库同步：`5dbaa4b..fc6c3d1 main -> origin/main`

## 三、实测闭环（方舟 lite 端点 ep-20261013070524-xjjn2）

```
[07:31:38] === worker process start ===   ← v3.4 进程（md5 4b6fcba7 核对无误）
[07:32:38] TASK START  2026-10-13-stream-verify.md (92 chars)
[07:32:38] TASK MODEL  -> ep-20261013070524-xjjn2     ← lite 分级正确
[07:32:41] TASK LLM OK ... tokens=?                    ← 流式聚合成功；方舟流式不返回 usage，走降级不报错
[07:32:41] TASK DONE    -> done/2026-10-13-stream-verify.md.result.md
```

- 结果文件内容合格：密度函数标准解释，无 `<seed:think_*>` 泄漏、无凭据泄漏
- 本时段零 ERROR（日志仅存 07:13–07:15 两条 404 历史遗留，v3.2 已修复）
- `ai-worker` 服务 active

**诚实记录一次小插曲**：任务文件首次落位后，旧版 v3.3 worker 于 07:31:16 抢先收走处理（非流式路径）；重启加载 v3.4 后清理无效产物、重新派发，上述时间线为 v3.4 真实流式路径。教训：worker.py 热替换与任务派发之间必须**先重启、后派发**。

## 四、收益诚实备注

- 首 token 延迟降低、体感更顺；**总完成时间提升有限**
- 真正价值：为后续并发调用、长任务流式输出铺路；错误上抛语义与降级路径均已验证

## 五、遗留

- API Key 轮换（用户去方舟控制台重建后，我更新 .env + 重启 + ping 复验）
- GitHub 仓库地址到位后 `git remote add origin + push`（CI 已预改 27）
