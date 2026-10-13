# 山水工程 Shanshui · 超级地形调度器

让 Minecraft 一个世界里**多个地形引擎按随机掩码分区共存**的 Fabric mod——A 区是 UltraTerraForged 的写实地形，B 区是 Tectonic 的山脉，C 区是原版，区域之间可渐变 / 断层 / 海面掩蔽过渡，而不是只能二选一。

## 当前状态

| 里程碑 | 状态 |
|---|---|
| v4 数据包格式修复（pack.mcmeta / base_octave / dimension_type） | ✅ 完成 |
| v5 两区缝合（Tectonic × 原版） | ✅ 构建成功，jar 已装入 mods，**待游戏内实测** |
| v6 三区缝合（+ UTF） | ⏳ 侦查完成，方案待定（UTF 自定义 density function 类型运行时注册是最大风险点） |
| M3 分区预览图 | ⏳ 待办 |
| 掩码种子校准 | ⏳ `poc/mask_map.py` 就绪，待飞点回报 |
| 4064 高度运行时验证 | ⏳ 待办（最高风险点） |

## 工作原理

在创建世界界面注入 **Customize 标签页**（滑块调地形调度参数）→ 参数渲染成标准数据包 `zz_hybrid_scheduler` 注入世界 → 在 density function 层完成缝合：

```
final_density = lerp(mask01, minecraft:overworld/final_density, hybrid:vanilla/final_density)
                    ▲                    ▲                          ▲
              掩码(0~1)          Tectonic 引擎(被mod覆盖)      原版引擎(内嵌副本)

mask ≈ 0 → 原版引擎生效；mask ≈ 1 → Tectonic 引擎生效；中间值 → 渐变过渡
```

## 技术栈

- Minecraft 26.3（预去混淆，官方类名）+ Fabric Loader 0.19.5 + Fabric API
- fabric-loom 1.19.0-alpha.2 + Gradle 9.8.1 + **JDK 27**（toolchain 27 编译，`options.release = 25` 产物字节码向下兼容 Java 25，major 69）
- GPL-3.0

## 构建

```bash
# 需要 JDK 27（产物字节码目标 Java 25，玩家运行时零影响）
gradle build
# 产物：build/libs/*.jar → 放入实例 mods/ 目录
```

## 文档

- [`山水工程-交接说明.md`](山水工程-交接说明.md) — 完整交接文档（项目全貌、进度、技术细节、待办）
- [`山水工程-工程指南.md`](山水工程-工程指南.md) — 简短记忆锚点

## 硬约束

- 世界高度 4064；海平面 63
- 不加方块 mod、不用无 26.3 版本的 mod
- 现有整合包 mod 全部保留
