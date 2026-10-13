# 山水工程 AI Worker · 网络白名单（出站允许）

> 状态：**软白名单**（2026-10-13 部署）——本清单记录 + worker 自律（FORBIDDEN 黑名单 + AI 铁律）。
> 硬防火墙（ufw 出站白名单）**未实施**，待总工批准后启用——防止误锁 apt/方舟把服务器锁死。
> 本文件由总工任务书部署，记录 ONBOARDING §7 允许域清单。

## 允许域

| 域 | 用途 |
|---|---|
| `ark.cn-beijing.volces.com`、`*.volces.com` | 方舟 API（模型调用） |
| `github.com`、`api.github.com`、`raw.githubusercontent.com`、`*.githubusercontent.com` | GitHub 只读（无凭据） |
| `modrinth.com`、`curseforge.com`、`mcmod.cn`、`*.mcmod.cn` | MC 模组生态（研究素材） |
| `repo.maven.apache.org`、`repo1.maven.org`、华为云/腾讯云镜像 | Gradle/Maven 依赖 |
| `archive.ubuntu.com`、`security.ubuntu.com`、`azul.com`、`*.azul.com` | apt / Azul JDK |
| `pypi.org`、`files.pythonhosted.org` | Python 包 |
| SMTP 服务器域（.env 的 MAIL_HOST） | 邮件汇报 |

## 连通性自检（2026-10-13 部署时实测）

| 域 | 结果 |
|---|---|
| 方舟 API `ark.cn-beijing.volces.com/api/v3` | ✅ 401（0.15s，无鉴权正常表现，链路通） |
| GitHub `github.com` | ✅ 200（0.69s） |
| PyPI `pypi.org` | ✅ 200（0.31s） |

> 自检命令：`curl -s -o /dev/null -w '%{http_code} (%{time_total}s)' --max-time 10 <url>`
> 判定口径：任何 HTTP 状态码（含 401/403）= 链路通；000 / 超时 = 不通。
