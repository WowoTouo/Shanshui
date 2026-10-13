# MODEL-REGISTRY.md — 山水模型注册表与记忆库

> 记录山水用过的每个模型（配置/消耗/表现/教训）与候选白嫖模型清单；换模型一键切换
> 配套 FOUNDATION §三「模型无关化设计」；每次切换追加「模型记忆」条目 + CHRONICLE 留痕
> 权威主文件随基石同步：服务器 `/home/agent/MODEL-REGISTRY.md` = 本地 `coordination/` = Gitee/GitHub

---

## 当前模型（记忆快照 2026-10-13）

| 项 | 值 |
|---|---|
| 供应商 | 字节跳动 · 火山方舟（ARK） |
| 模型 | **Doubao-Seed-Evolving**（08.27 升级版） |
| endpoint（PRO） | `ep-20261013070524-xjjn2` |
| endpoint（LITE） | `ep-...-lite`（.env ARK_MODEL_LITE） |
| 单价 | 6.0 元/百万 tokens |
| 余额快照 | **4,963,479 / 5,500,000 tokens**（2026-10-13；≈29.8 元） |
| 配额池 | 山水 + 科学共用同一 endpoint（非独立账户） |
| 日均消耗 | 估 6-12 万 tokens（0.4-0.7 元/天）→ 可跑 40-80 天 |
| 调用参数 | temperature 0.3 / max_tokens 4096 / stream=True |
| 告警 | quota-alert.sh 每 6h 估算，<100 万 tokens 邮件告警 |

---

## 架构：OpenAI 兼容 = 模型无关

worker.py 经 **OpenAI 兼容端点**调用（`client.chat.completions.create`，流式），
**换模型零代码改动**，只改 `.env` 三键：

```bash
# /home/agent/.env（600）
ARK_API_KEY=<新模型 API Key>       # 键名不变，语义 = LLM_API_KEY
ARK_BASE_URL=<新模型 base_url>      # 例 https://api.siliconflow.cn/v1
ARK_MODEL_PRO=<新模型名>            # 例 deepseek-ai/DeepSeek-V3（LITE 同理）
```

## 一键切换（复活步骤，约 2 分钟）

1. 编辑 `/home/agent/.env`（600）改上述三键
2. `sudo systemctl restart ai-worker`
3. 验证：`tail /home/agent/logs/worker.log` → 见 `GUIDES loaded`（四层注入正常）
4. 派自检任务卡（任务名 `selfcheck-<新模型名>`），确认输出格式符合预期
5. 完成 → 本文件追加「模型记忆」条目 + CHRONICLE 留痕 + 锁板 release

## 候选白嫖模型（OpenAI 兼容，2026-10 评估）

| 模型 | 接入 base_url | 免费/低价 | 上下文 | 备注 |
|---|---|---|---|---|
| **SiliconFlow 硅基流动** | `https://api.siliconflow.cn/v1` | 有免费额度 | 32k+ | **白嫖首选候选** |
| 智谱 GLM-4 / GLM-4-Flash | `https://open.bigmodel.cn/api/paas/v4` | 新用户赠送 | 128k | 国内直连快 |
| 通义 Qwen（千问） | `https://dashscope.aliyuncs.com/compatible-mode/v1` | 有免费额度 | 32k+ | 阿里系 |
| DeepSeek-V3/R1 | `https://api.deepseek.com/v1` | 低价非免费 | 64k-128k | 便宜稳定 |
| Kimi（Moonshot） | `https://api.moonshot.cn/v1` | 无免费 | 128k | 偏贵 |
| **Ollama 本地** | `http://localhost:11434/v1` | **真免费** | 视模型 | 需内存/GPU；纯白嫖终极方案 |

> 免费额度政策随时变动，切换前以各官网为准。选型硬约束：OpenAI 兼容 + 上下文 ≥32k（指南注入 15k chars）+ 能稳定遵循任务输出格式。

## 模型记忆（历史条目）

### M1: Doubao-Seed-Evolving（2026-10-13 起，v3.7 部署后）
- **表现**：四层注入稳定；STALL 守卫 / 清理循环 / 提案通道三件套配合良好；自主派发与配额熔断机制验证通过
- **事件**：10-13 旧版死循环烧穿当日配额（count 12→0），v3.7 STALL 守卫根因兜底后重置恢复
- **教训**：方舟 `usage` 端点 404（无 AK/SK 查不了精确余额）→ 只能日志估算监控（quota-alert.sh）
- **切换触发条件**：quota-alert 告警（估算 <100 万 tokens）或免费额度耗尽 → 按上面一键切换
