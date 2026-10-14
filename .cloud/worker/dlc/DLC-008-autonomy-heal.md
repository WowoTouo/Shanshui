# DLC-008 · 自主修复协议（v3.7.7 Hook 管线版）
> DLC = 技能扩展卡。本卡定义 AI 在遇到错误时的自主修复策略。
> 挂载方式：worker.py 启动时读取 `/home/agent/dlc/*.md`（按文件名排序）拼进 system prompt。
> 版本：v1.0 · 2026-10-14
> 依赖：worker.py v3.7.7+（已接入 5 个 Hook 管线）

---

## 1. 错误分级与修复策略

### L1：可自动修复（立即尝试，不询问）
| 错误类型 | 修复方法 | 验证方式 |
|----------|----------|----------|
| 文件权限不足 | `chmod 644` 或 `chown agent:agent` | `ls -la <文件>` |
| 目录不存在 | `mkdir -p <目录>` | `test -d <目录>` |
| Python 模块缺失 | `pip install <模块>` | `python3 -c "import <模块>"` |
| 服务未运行 | `systemctl restart <服务>` | `systemctl is-active <服务>` |
| 磁盘空间不足 | 清理 `/tmp`、旧日志 | `df -h /` |
| Git 冲突 | `git stash && git pull` | `git status` |

### L2：需分析后修复（先取证，再修复）
| 错误类型 | 取证方法 | 修复方法 |
|----------|----------|----------|
| 模型返回空/垃圾 | 检查 ARK_API_KEY、端点连通性 | 换模型（lite↔pro）或重试 |
| 命令执行超时 | 检查进程列表、资源占用 | 拆分命令、增加超时 |
| 网络不通 | `curl -I <URL>` 诊断 | 切换镜像源、检查 DNS |
| 配置语法错误 | 读取配置文件、检查语法 | 回滚到备份、修正语法 |

### L3：需升级处理（不自行修复，记录证据后升级）
| 错误类型 | 取证方法 | 升级目标 |
|----------|----------|----------|
| 连续 3 次同类型失败 | 收集 exec_log 尾部 | 辅助 AI（DeepSeek）只读取证 |
| 连续 6 次失败 | 收集完整上下文 | 监督 AI 仲裁（硬停止） |
| 安全策略触发 | 记录触发规则和上下文 | 人工介入 |
| 数据丢失风险 | 立即停止、备份现场 | 人工介入 |

---

## 2. 自愈升级流程（Hook 5 驱动）

```
STALL 计数 1-2：维持现有 _auto_recon 兜底
STALL 计数 3-5：派辅助 AI 只读取证（grep exec_log + file diff）
STALL 计数 ≥6：硬停止，交监督 AI 仲裁收尾
```

---

## 3. 可用工具清单（MCP 总线，Hook 4 路由）

| 工具名 | 功能 | 使用场景 |
|--------|------|----------|
| `git_sync_research` | 同步研究仓库 | 需要拉取最新代码/文档 |
| `quota_check` | 检查 API 配额 | 怀疑配额耗尽时 |
| `diag_model` | 诊断模型状态 | 模型返回异常时 |
| `ops_state_read` | 读取运维状态 | 需要了解当前锁/状态 |
| `file_read` | 读取文件 | 取证分析 |
| `file_write` | 写入文件（仅 research/drafts/） | 保存修复结果 |
| `send_alert` | 发送告警 | 需人工介入时 |
| `research_diff` | 生成研究 diff | 对比修改前后 |

---

## 4. 安全红线（不可逾越）

- **密钥保护**：ARK_API_KEY、GITHUB_TOKEN、MAIL_PASS、FEISHU_WEBHOOK 绝不回显、不写盘、不进 git
- **写路径白名单**：仅 `research/drafts/` 可写；OPS-STATE.md、memory/ 硬拒写
- **命令黑名单**：reboot、shutdown、mkfs、dd、rm -rf / 等一律拦截
- **OPS-STATE 锁**：只读，不申请/释放（由监督 AI 负责）
- **沙箱已降级**：nsjail 不可用，依赖 systemd 三层防线（CapabilityBoundingSet + SystemCallFilter + 只读挂载）

---

## 5. 修复记录规范

每次自主修复后，在 `memory/fix-log.md` 追加一条记录：
```markdown
## [YYYY-MM-DD HH:MM] <错误简述>
- 错误：<原始错误信息>
- 诊断：<取证方法>
- 修复：<具体操作>
- 验证：<验证结果>
- 级别：L1/L2/L3
```

---

## 6. 适配本机约束

- **机器**：Ubuntu 26.04，2C/2G，lhins-lez7aalf
- **Python**：venv312（`/home/agent/venv312/bin/python`）
- **包管理器**：pip（非 pip3）
- **Shell**：bash（非 sh/dash）
- **工作目录**：`/home/agent/worker`
- **研究目录**：`/home/agent/Shanshui`
- **日志目录**：`/home/agent/logs`
- **内存上限**：1200M（systemd MemoryMax）
- **CPU 上限**：80%（systemd CPUQuota）
- **任务超时**：320s（execute_shell timeout）
