# 研究方向队列（research-backlog）

> 总工维护优先级；AI 自主模式按序认领（跳过 [✔]）。
> AI 可追加 `[?]` 建议项（需总工批准升级为正式项）。
> 状态图例：`[ ]` 未开始  `[~]` 进行中  `[!]` 阻塞（须附原因）  `[✔]` 完成  `[?]` 待批建议

## 正式队列

1. [ ] Tectonic `final_density` 语义取证：输入/输出语义、取值范围、能否被外部调度器改写（结论须含可引用证据：文件路径+代码行）
2. [ ] v6 三区缝合风险：UTF 自定义 df 类型 `ultraterraforged:cell` / `clamp_to_nearest_unit` 在 MC 26.3 的注册可行性；26.3 原生 df 类型注册表全集核对（CFR 反编译 merged jar）
3. [ ] 掩码调度设计：区块级随机掩码（zz_hybrid_scheduler）、区域边界模式（GRADIENT/CLIFF/SEA_MASK/NEIGHBOR_AVG）、山区引擎占大区块的权衡分析
4. [ ] 世界高度 4064：Tectonic `set_height_limits` 是否覆盖 4064（最高风险点，结论直接影响 v6 架构）
5. [ ] M3 预览图方案：创建世界界面显示引擎分区预览（参考 UTF TerrainPreview：后台采样 + DynamicTexture），输出技术方案文档

## 建议区（AI 追加，待总工批准）

<!-- AI 在此行下追加 [?] 建议项，格式：- [?] <建议一句话>（理由） -->
