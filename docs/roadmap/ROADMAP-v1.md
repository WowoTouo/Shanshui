# 山水工程 Shanshui · 超级地形调度器 — 第一版任务大纲

> 创建时间：2026-10-15
> 状态：Phase 0 — 调研与架构设计
> 仓库：https://github.com/WowoTouo/Shanshui

---

## 一、项目定义

### 1.1 核心目标

做一个 **Fabric mod**（MC 26.3 / Mojang mappings），让 Minecraft 一个世界里**多个地形引擎模组按随机掩码分区共存**，使玩家同时体验到多种地形。

### 1.2 第一版成果形态（v1.0 MVP）

| 功能 | 描述 | 优先级 |
|------|------|--------|
| 多引擎共存 | 至少支持 2 个地形引擎 + 原版在同一世界中共存 | P0 |
| 随机掩码分区 | 按 chunk 粒度分配地形引擎，支持可配置的掩码规则 | P0 |
| 区域过渡 | 区域边界实现基本的渐变过渡（density function lerp） | P0 |
| 高度限制破解 | 突破原版 256 格高度限制 | P1 |
| 配置文件 | JSON/YAML 配置地形引擎分配规则 | P1 |
| 兼容性 | 与主流 Fabric mod 生态兼容 | P1 |

### 1.3 技术栈

- **MC 版本**：26.3（Mojang mappings 预去混淆）
- **Mod 框架**：Fabric Loom
- **构建工具**：Gradle
- **JDK**：25
- **核心机制**：density function 层 lerp(mask, engineA, engineB)

---

## 二、研究阶段（Phase 0：当前）

### 2.1 外部调研

| 序号 | 研究主题 | 目标 | 状态 |
|------|----------|------|------|
| R1 | 同类 AI 技能包项目分析 | 学习 mattpocock/skills、addyosmani/agent-skills 等设计模式 | ⏳ |
| R2 | MC 地形生成原理 | 理解 density function、chunk generator、noise router | ⏳ |
| R3 | UltraTerraForged 源码分析 | 理解其地形生成流程和可拦截点 | ⏳ |
| R4 | Tectonic 源码分析 | 理解其山脉生成算法和参数 | ⏳ |
| R5 | TerraBlender 架构参考 | 学习多 biome 共存的分层设计 | ⏳ |
| R6 | 原版高度限制机制 | 分析 height limit 的实现和破解方案 | ⏳ |

### 2.2 知识沉淀

- 所有研究产物存入 `/home/agent/Shanshui/docs/research/`
- 关键发现写入 `/home/agent/Shanshui/learnings/`
- 可复用的代码片段存入 `/home/agent/Shanshui/playbooks/`

---

## 三、开发阶段（Phase 1-3）

### Phase 1：核心原型

| 里程碑 | 交付物 | 验收标准 |
|--------|--------|----------|
| M1.1 | 项目骨架 | Gradle 构建通过，Fabric 入口点注册成功 |
| M1.2 | 掩码系统 | 按 chunk 坐标生成确定性掩码值 |
| M1.3 | 引擎路由 | 根据掩码值调用不同地形引擎的 density function |
| M1.4 | 双引擎共存 | 原版 + 1 个第三方引擎在同一世界生成地形 |

### Phase 2：过渡与优化

| 里程碑 | 交付物 | 验收标准 |
|--------|--------|----------|
| M2.1 | 区域过渡 | 边界 chunk 实现 lerp 渐变 |
| M2.2 | 海面掩蔽 | 海洋区域自动平滑过渡 |
| M2.3 | 高度扩展 | 突破 256 格限制，支持 384+ 格 |
| M2.4 | 性能优化 | 掩码计算零开销，chunk 生成延迟 < 原版 1.2x |

### Phase 3：完善与发布

| 里程碑 | 交付物 | 验收标准 |
|--------|--------|----------|
| M3.1 | 配置文件 | JSON 配置地形引擎分配规则 |
| M3.2 | 三引擎共存 | 原版 + 2 个第三方引擎共存 |
| M3.3 | 兼容性测试 | 与 20+ 主流 Fabric mod 兼容 |
| M3.4 | 发布 v1.0 | CurseForge / Modrinth 发布 |

---

## 四、AI 训练计划

### 4.1 训练目标

让 SSHE 结构中的 3 个 AI 充分理解 MC 地形生成原理，具备独立研究和开发能力。

### 4.2 训练步骤

1. **知识注入**：将研究资料写入 DLC 扩展卡和 learnings/ 知识库
2. **实战演练**：通过任务文件驱动 AI 分析源码、编写原型代码
3. **迭代优化**：AI 自检 → 监督 AI 审核 → 辅助 AI 重验证
4. **能力沉淀**：成功经验写入 playbooks/，失败教训写入 learnings/

---

## 五、当前行动项（2026-10-15）

| 序号 | 行动 | 负责人 | 截止 |
|------|------|--------|------|
| A1 | 创建研究目录结构 | AI Shan | 今天 |
| A2 | 搜索同类 AI 技能包项目 | AI Shan | 今天 |
| A3 | 分析 UltraTerraForged 源码结构 | AI Shan | 本周 |
| A4 | 分析 Tectonic 源码结构 | AI Shan | 本周 |
| A5 | 编写 density function 拦截原型 | AI Shan | 本周 |
| A6 | 研究原版高度限制破解方案 | AI Shan | 本周 |

---

> 本文档由 SSHE 三 AI 结构协作维护，每次重大进展后更新。
