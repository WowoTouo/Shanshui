model: pro

# 任务：分析 Tectonic 3.0.31 的 final_density 语义

## 背景
山水工程 v6 三区缝合方案需要吃透 Tectonic 的 final_density 结构。本地已有部分侦查数据，但你（服务器 AI）需要独立取证，结论将决定 lerp 缝合的参数对齐方式。

## 要求
1. 获取 Tectonic（Tectonic: Dimensions 或 tectonics mod，MC 1.20.2 Fabric 版，版本 3.0.31 或最接近的 1.20.2 兼容版）jar：从 Modrinth 或 CurseForge 下载（可用 aria2c 多线程）
2. 解压分析 `data/tectonic/worldgen/density_function/` 下的 final_density 及其上游依赖
3. 逐条回答：
   - Tectonic 的 final_density 输出值域是什么（-1~1 还是 0~1 或其他）？与 minecraft:overworld/final_density 的值域一致吗？
   - 两者的 noise_settings（base_octave / top_slide / bottom_slide / 高度参数）是否一致？不一致时 lerp 直接缝合会出现什么视觉后果（地面悬空/海水倒灌/地形撕裂）？
   - Tectonic final_density 的完整上游依赖树是什么（列出直接依赖链）
   - 若要把它作为 lerp 的 B 引擎，最小需要的对齐改造有哪些？
4. 产出格式：markdown，800 字以内，硬核直球，结论先行

## 约束
纯研究任务：只读分析，不写代码、不改仓库。证据（jar 下载地址、文件路径、关键 json 片段）要附上。
