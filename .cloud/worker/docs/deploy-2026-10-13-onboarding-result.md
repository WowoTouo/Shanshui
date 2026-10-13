# ONBOARDING 开机记忆 + sudoers v4 + 网络白名单 · 验收报告（2026-10-13）

> 执行说明：本任务书涉及改 worker.py 自身代码 + sudoers（visudo 在 AI 黑名单、仓库对 AI 只读是铁律）——服务器 AI 按设计碰不了，由总工侧执行（与流式化波一致）。

## 一、入职指南部署（开机记忆）

| 项 | 状态 |
|---|---|
| `/home/agent/ONBOARDING.md` | ✅ 7425 字节，644，agent 所有（源本存档 `.cloud/worker/ONBOARDING.md`，commit `9f7c2e1`） |
| worker.py v3.5 改动 | ✅ `load_onboarding()`（缺失/为空/读失败 → '' 安全降级，不写日志防单测炸）+ `build_system_prompt()`（内置 prompt + 指南拼接）+ `SYSTEM_PROMPT_EFFECTIVE` 进程内固化；`main()` 在 `load_env()` 后只读一次并刷新 |
| 降级路径 | ✅ 单测 [9]/[9b]/[9c]/[9d] 四分支（文件在/拼接/缺失降级/读失败降级），本地 **29 项全过** |
| 服务器 py_compile | ✅ venv312（Python 3.12）过；worker.py md5 `c49187ce` 与本地一致 |

**worker 日志关键行（开机记忆生效实锤）**：
```
[2026-10-13 07:42:49] === worker process start ===
[2026-10-13 07:42:49] ONBOARDING loaded (4201 chars) -> system prompt（开机记忆生效）
```

设计要点：只读一次、进程内固定——system 保持静态，上下文缓存仍命中。

## 二、sudoers 权限矩阵 v4

流程：`visudo -c -f` 预校验 → 旧版备份 `/root/sudoers-agent-worker.bak-20261013` → `install -o root -g root -m 0440` → 全量 `visudo -c` 通过（可逆）。

**agent 有效权限（`sudo -l -U agent` 实证，共 15 条）**：

| 类别 | 命令 |
|---|---|
| 包安装（原有） | `apt-get install *`、`apt install *`、`apt-get update`、`apt update` |
| 自身服务（原有） | `systemctl restart/start/stop/status/is-active ai-worker` |
| 日志轮转（原有） | `logrotate *` |
| **工具链（v4 新增）** | `curl`、`wget`、`unzip`、`tar`、`aria2c`（5 个路径均实证存在于 /usr/bin/） |

**明确未增加**：任何删除/覆写/网络配置/用户管理命令。

## 三、网络白名单（软实施）

- `/home/agent/work/network-whitelist.md` 已建（1520 字节）：记录 ONBOARDING §7 全部允许域（方舟/GitHub/MC 模组生态/Maven 镜像/apt+Azul/PyPI/SMTP）
- **硬防火墙未实施**（ufw 出站白名单待总工批准）——防误锁 apt/方舟
- **三域连通实测**：方舟 `401`（0.15s，无鉴权正常表现）/ GitHub `200`（0.69s）/ PyPI `200`（0.31s）——全通

## 四、自检任务闭环（AI 知道自己是谁）

```
[07:43:50] TASK START  2026-10-13-onboarding-recall.md (251 chars)
[07:44:09] TASK LLM OK  ... tokens=?          ← 流式模式，方舟不返回 usage，预期降级
[07:44:09] TASK DONE
```

AI 回答要点（19 秒闭环）：身份=山水工程专职研究员 AI（腾讯云轻量服务器）；项目=MC 26.3 Fabric 超级地形调度器（三引擎随机掩码 + density function 层 lerp 缝合）；§4 权限矩阵准确回忆 **8 类可做 / 5 类硬禁**（含「aria2c 多线程」「无 push 凭据」细节）；【结论】段置顶符合汇报纪律；只读任务未执行任何命令。

## 五、残留风险与遗留

**已知并接受的残留风险**：`curl`/`wget`/`tar`/`unzip` 作为 root 有能力写任意路径（`curl -o` / tar 路径穿越）。当前靠三层联防：worker.py FORBIDDEN 黑名单 + systemd 沙箱（SystemCallFilter=@system-service）+ AI 铁律（ONBOARDING §3）。硬防火墙批准后风险面进一步收敛。

**遗留（未变）**：
1. API Key 轮换（控制台重建后我更新 .env + 重启 + ping 复验）
2. GitHub 仓库地址（唯一阻塞项）
3. 硬防火墙（ufw 出站白名单）待总工批准

**改动清单**：commit `9f7c2e1`（v3.5 + ONBOARDING.md + network-whitelist.md + sudoers-agent-worker 源本）+ 本报告；服务器仓库待同步。
