PYEOF
echo "patcher written: $(wc -l < /home/agent/work/patch_v372.py) lines"
```

## 步骤 2／4：应用补丁（自动备份 + 4 处锚点替换 + 编译闸）
```bash
python3 /home/agent/work/patch_v372.py /home/agent/worker/worker.py
```
判定：
- 输出含 `DONE` 且 `PYCOMPILE OK` → 进步骤 3
- 输出含 `ABORT` / `MISS` / `PYCOMPILE FAIL` → **立即停止**：把完整输出写进 result，**不要重启**，结束任务

## 步骤 3／4：验证补丁行为（导入打过补丁的 worker 断言）
```bash
python3 - <<'PYEOF'
import importlib.util
s = importlib.util.spec_from_file_location('w', '/home/agent/worker/worker.py')
w = importlib.util.module_from_spec(s); s.loader.exec_module(w)
r = w.strip_think_tags('<seed:think_x>完整答案内容</think_x>')
assert '完整答案内容' in r, 'FAIL: 整段思考块未回退'
assert '思考' not in w.strip_think_tags('前<seed:think_x>思考</think_x>后'), 'FAIL: 混合块未剥'
assert w.STALL_RETRY_AFTER == 6, 'FAIL: STALL 常量缺失'
print('VERIFY OK: 空结果回退 + STALL 自愈常量均在')
PYEOF
```
断言失败 → **回滚**：`cp /home/agent/worker/worker.py.bak-pre-v372 /home/agent/worker/worker.py`，result 写明回滚原因，不重启，结束。

## 步骤 4／4：写结论（**不重启**）
result 必含：
- 补丁应用 + 本地验证：通过 / 失败（附完整输出）
- 备份位置：`/home/agent/worker/worker.py.bak-pre-v372`
- **未重启**（遵铁律⑤：重启 live 服务属重大变更，留总工确认）。补丁已写盘，将在下次重启生效——每日重生 ≤24h 自动加载，或总工下令重启 / 发展代劳。
- 复盘一句：bug1（空结果）是因，bug2（STALL 卡死）是果；修复后 result 不再空、自主派发有产出即会更新状态行自愈。

## 红线（违反即违纪）
1. **不重启 ai-worker**（重启 = 部署铁律「先 restart 后派发」，由发展 / 总工执行）
2. **不 git commit / push**（代码仓库对你只读；补丁落仓库由发展同步）
3. 编译不过 / 断言不过 → 立即回滚，绝不带病留盘
4. 本授权仅限这次 v3.7.2 双 bug 补丁，不代表今后可自改代码
