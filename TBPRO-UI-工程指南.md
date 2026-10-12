# TBPRO-UI 工程指南（记忆锚点）

> **用途**：本文件是 TBPRO-UI 项目的唯一权威状态记录。AI 上下文压缩/丢失后，先读本文件再动手。
> **最后更新**：2026-10-13（v5 缝合版构建成功：Tectonic×原版掩码分区，build10，jar 52.4KB 已装入 mods 待实测）
> **工程根目录**：`D:\窝窝头的1.20.2整合包\TBPRO-UI\`

---

## 0. 一句话项目

自研 Fabric mod「TBPRO UI」：在 MC 26.3 创建世界界面加入 Customize 标签页（滑块调地形调度参数 + 引擎分区预览），创建时把参数渲染成 `zz_hybrid_scheduler` 数据包注入世界，实现"多地形引擎（UTF + Tectonic + 原版）按大尺度随机掩码分区共存"的超级地形调度器。

## 1. 用户硬约束（验收标准，不可违背）

- 世界高度 **4064 默认**（Extended World Height 4064 / Higher Heights 4064，用户拒绝每次手动换预设）
- 海平面：默认 63 不动（用户曾提"海平面-60"，后改口"可以抬高一点点"，最终定 63）
- 边界不要求渐变——可自然悬崖/断层/海面掩蔽/区块均值（BoundaryMode：GRADIENT/CLIFF/SEA_MASK/NEIGHBOR_AVG）
- 山区引擎应占更大区块（掩码频率/区块大小可调）
- **拒绝加新方块 mod、拒绝无 26.3 版本的 mod**；现有整合包 mod 全部验证可用且**禁止删除**
- 代码可开源（GPL-3.0 LICENSE 已写）
- 回复风格：硬核直球、纯文本分点、不用链接、不解释直接给配置
- 用户 PC：i7-10750H / RTX2060 6G / 16G，目标拍建筑视频 60fps+氛围

## 2. 已完成里程碑

| # | 内容 | 状态 |
|---|---|---|
| 1-3 | 全局粒子/特效/实体降载（particle_core、particular、动态光源、掉落物物理等，maxParticlesPerSheet 512/256、全局 0.4） | ✅ |
| 4 | 反编译 UTF（ultraterraforged-1.0.1+26.3.jar，744 class → `poc/learn/utf_decomp/`）学习 terrain 界面架构 | ✅ |
| 5 | 架构设计文档 `C:\Users\CHN_W\Doubao\chats\2026-10-07\new-chat\TBPRO-UI-架构设计.md` | ✅ |
| 6 | 构建环境打通 + 首版代码编译成功（build8，24s，jar 41.1KB） | ✅ |
| 7 | 数据包 26.3 格式修复（v4：pack.mcmeta 加 min/max_format、noise 改 base_octave、dimension_type 重排、去 smoothstep） | ✅ |
| 8 | **v5 超级缝合：Tectonic×原版掩码分区**（原版 27 df 转 hybrid:vanilla + mask01 归一化 + final_density lerp） | ✅ 已装待实测 |
| 7 | **游戏内实测**（创建世界界面出现 TBPRO 标签、建世界验证地形） | ⏳ 未做 |

## 3. 构建环境完整答案（26.3 生态，全验证）

### 版本矩阵
- MC **26.3**（java_version=25，Mojang 停发官方 mappings，jar 预去混淆）
- Fabric Loader **0.19.5** / Fabric API **0.162.0+26.3**
- Loom 插件：**`id 'net.fabricmc.fabric-loom' version '1.19.0-alpha.2'`**（26.1+ 未混淆专用；老 `fabric-loom` 只兼容混淆版且要 mappings）
- Gradle **9.8.1**（华为云镜像 `mirrors.huaweicloud.com/gradle/gradle-9.8.1-bin.zip`，3.7MB/s）
- JDK：`D:\JAVA21orPython\JAVA25\jdk-25.0.3.9-hotspot`（JAVA_HOME 同路径）
- gradle.properties 含 `org.gradle.java.installations.paths=同上`

### build.gradle 关键配置（当前生效版）
```groovy
plugins {
    id 'net.fabricmc.fabric-loom' version '1.19.0-alpha.2'
    id 'maven-publish'
}
dependencies {
    // 无 mappings 行！无 modImplementation！
    minecraft "com.mojang:minecraft:26.3"
    implementation "net.fabricmc:fabric-loader:0.19.5"
    implementation "net.fabricmc.fabric-api:fabric-api:0.162.0+26.3"
}
```

### 构建命令
```powershell
$env:JAVA_HOME="D:\JAVA21orPython\JAVA25\jdk-25.0.3.9-hotspot"
$env:Path="$env:JAVA_HOME\bin;$env:Path"
Set-Location "D:\窝窝头的1.20.2整合包\TBPRO-UI"
& "D:\JAVA21orPython\GRADLE\gradle-9.8.1\bin\gradle.bat" build --no-daemon
# 产物：build\libs\tbpro-ui-0.1.0.jar
# 增量构建约 14-24s（MC/Loom 已缓存到 C:\Users\CHN_W\.gradle\caches\fabric-loom\26.3\）
```
- 加速：去掉 `--no-daemon` 用常驻 daemon、`-x test`、只跑 `jar` 任务
- 部署：拷 jar 到 `D:\窝窝头的1.20.2整合包\.minecraft\versions\26.3-Fabric 0.19.5\mods\`

### 踩坑史（勿重踩）
1. Loom 1.18.4 要求 Gradle ≥9.7 → 升 9.8.1
2. Loom 找 `officialMojangMappings()` → 26.3 无官方映射 → **删 mappings 行**
3. `Configuration 'mappings' has no dependencies` → 老插件 ID 的问题 → **换 `net.fabricmc.fabric-loom`**
4. `modImplementation()` 不存在 → 未混淆 Loom 无 mod 配置 → **用普通 `implementation`**
5. API 差异（javap 确认）：AbstractSliderButton 无 getValue()（`this.value` protected 字段）；AbstractWidget.height 是 protected（用 `setHeight()`）；CycleButton.builder 的 messageProvider 返回 **Component**（不是 String）；CreateWorldScreen 的 `getDataPackSelectionSettings`/`tryApplyNewDataPacks` 是 private（**Accessor @Invoker**）

## 4. 代码地图（src/main/java/com/tbpro/）

```
TbproUI.java                        client 入口，MOD_ID=tbpro
settings/TbproSettings.java         record：maskFrequency/maskOctaves/bShare/boundary/seaLevel/worldHeight
                                   + serialize()/parse() 手写 JSON + BoundaryMode 枚举（4 模式中文 label）
                                   + DEFAULT：0.002f/-4/0.5f/GRADIENT/63/4064
gui/createworld/TbproState.java     Holder 接口 + settings/revision/active/pendingSelection/update(Consumer)
gui/createworld/TbproTab.java       标签页：6 控件（频率滑块/区块大小 CycleButton/B占比滑块/边界 CycleButton/海平面滑块/高度显示）
                                   SimpleSlider extends AbstractSliderButton（读 this.value）
gui/createworld/TbproApplier.java   prepareForCreate：参数→zip→临时目录→reload→setSelected→tryApplyNewDataPacks
data/TbproPacks.java                模板渲染（readResource + 占位符替换 + 目录 zip 打包）+ packName(SHA-1 12hex)
mixin/CreateWorldScreenMixin.java   @ModifyArg init→addTabs 数组扩容追加 TbproTab
                                   @Inject onCreate HEAD cancellable→TbproApplier（失败 toast+cancel）
                                   @Inject tick HEAD→TbproTab.tick + isReadyToCreate 后 schedule onCreate
mixin/CreateWorldScreenAccessor.java @Invoker 暴露 2 个 private 数据包方法
resources/
  fabric.mod.json                   depends：fabricloader≥0.19.5 / fabric-api / minecraft ~26.3
  tbpro.mixins.json                 client: CreateWorldScreenMixin + CreateWorldScreenAccessor
  assets/tbpro/lang/zh_cn.json, en_us.json
  templates/zz_hybrid_scheduler/    数据包模板（4 个 JSON 已占位符化）
```

### 模板占位符（templates/zz_hybrid_scheduler/）
- `data/hybrid/worldgen/noise/region_mask.json` → `{{maskOctaves}}`（base_octave）
- `data/hybrid/worldgen/density_function/region_mask.json` → `{{maskFrequency}}`（xz_scale）
- `data/minecraft/dimension_type/overworld.json` → `{{worldHeight}}`（logical_height/height）、`{{worldDepth}}`（min_y，= -(worldHeight/2)）
- `data/minecraft/worldgen/noise_settings/overworld.json` → `{{seaLevel}}`、`{{worldDepth}}`；final_density 引用 `hybrid:final_density`
- 静态文件（无占位符）：`data/hybrid/worldgen/density_function/vanilla/*`（27 个原版 df 副本，内部引用已改 `hybrid:vanilla/*`）、`mask01.json`（clamp(mul(add(mask,1),0.5),0,1)）、`final_density.json`（lerp(mask01, minecraft:overworld/final_density=Tectonic版, hybrid:vanilla/final_density=原版)）

### 26.3 数据格式事实（v4 踩坑，勿重踩）
- pack.mcmeta 必须含 `min_format`/`max_format`（pack_format>81 时），Tectonic 用 `supported_formats:[1,999], min_format:1, max_format:999`
- noise 定义：`base_octave`+`octave_count`+`amplitude_modifiers`（旧 `firstOctave`/`amplitudes` 已废）
- density function 类型只有：abs/add/max/min/mul/noise/sub（**无 smoothstep、无 lerp、无 clamp**——clamp 用 min/max 组合）
- dimension_type：`monster_spawn_light_level` 字段平铺（min_inclusive/max_inclusive 顶层）+ `has_ender_dragon_fight` + `default_clock` + `timelines` + `attributes` 块
- noise_settings 原版为引用式（noise_router 引用 minecraft:overworld/* 独立文件）；Tectonic 覆盖这些 df 命名空间（mod 数据包）
- **Tectonic 缝合原理**：`minecraft:overworld/final_density` 被 Tectonic mod 替换 → 引用它 = Tectonic 引擎；内嵌原版副本 `hybrid:vanilla/final_density` = 原版引擎；lerp(mask01, a, b) 分区
- **UTF 缝合（未做）**：UTF 的 df 是运行时 PresetPacks 生成（jar 无静态数据）——需走 UTF 预设流程提取生成 zip 再内嵌

## 5. 核心机制（学习自 UTF 反编译，全部对照过 26.3 API）

1. **界面注入**：Mixin CreateWorldScreen → `@ModifyArg` 拦截 `MenuTabBar$Builder.addTabs(Tab[])`（描述符 `addTabs([Lnet/minecraft/client/gui/components/tabs/Tab;)Lnet/minecraft/client/gui/components/tabs/MenuTabBar$Builder;`）数组扩容追加 TbproTab；`@Inject onCreate HEAD` cancellable，prepareForCreate 失败 → SystemToast（PACK_LOAD_FAILURE 存在）+ cancel
2. **参数→数据包**：TbproSettings → 模板渲染 zip → `screen.getDataPackSelectionSettings(...)` 返回临时目录 → 写入 → `repository.reload + setSelected` → `tryApplyNewDataPacks(repository, false, consumer)`（幂等：presetPacks(current) 与 wanted 相等直接 return true）
3. **Accessor**：`(CreateWorldScreenAccessor)(Object) screen` 调 @Invoker 方法
4. **预览（M3 未做）**：UTF 用后台 ScheduledExecutor + 150ms 防抖 → GeneratorContext 采样 → 256×256 int[] → DynamicTexture → 滚轮缩放/拖拽平移（照抄 TerrainPreview）

## 6. 当前状态与待办（下一步从这里继续）

### 刚完成
- build8 **BUILD SUCCESSFUL**（24s），`tbpro-ui-0.1.0.jar`（41.1KB）已装入 mods 目录
- 全部注入点 javap 核对匹配 26.3

### 待办（按优先级）
1. **游戏内实测**（最高优先）：用户启动 → 创建世界界面 → 确认 TBPRO 标签出现 → 调参建世界 → 验证地形分区。若崩溃/无标签 → 收错误报告修复（Mixin 注入点是运行时解析，编译通过≠运行成功）
2. **Tectonic 编入调度器**：当前模板 overworld.json（207KB）是 UTF×原版 lerp，0 处 tectonic 引用；v3 数据包 `...\26.3-Fabric 0.19.5\datapacks\zz_hybrid_scheduler\` 同款。Tectonic 3.0.31 fabric 已装（Modrinth `lWDHr9jE`）+ Lithostitched 2.0.5。**做法**：把 Tectonic 的 density_function 加入 lerp 槽（参考 Tectonic jar 内 `resourcepacks/tectonic/data/minecraft/worldgen/noise_settings/overworld.json`）
3. **M3 预览图**：照 UTF TerrainPreview 实现（后台采样 + DynamicTexture + 缩放/平移 + 悬停坐标）
4. **引擎掩码种子校准**：`poc/mask_map.py`（MC 26.3 Perlin/Xoroshiro 移植，10 候选派生）已就绪，输出 `C:\Users\CHN_W\Doubao\chats\2026-10-07\new-chat\mask_maps\`（seed 12345）；需用户飞点回报哪个候选正确
5. **4064 运行时验证**：Tectonic set_height_limits 是否覆盖 4064 未实测（最高风险点）；F3 看世界底部 Y / setblock 上限
6. **海平面最终值**：当前 63 按默认不动（用户可再调）

### 相关数据包（实例目录 `...\26.3-Fabric 0.19.5\datapacks\`）
- `zz_hybrid_scheduler\`（v3，pack_format 108，sea_level 63，min_y -2032，UTF×原版）
- `lower_sea_level\`、`ultraterraforged_4064\`（历史方案）

### 用户环境（勿动）
- 实例根：`D:\窝窝头的1.20.2整合包\.minecraft\versions\26.3-Fabric 0.19.5\`
- 启动器：`D:\窝窝头的1.20.2整合包\Aer晨1.20.1生活大冒险整合包(1)\Plain Craft Launcher 2.exe`
- 最终 JVM：`-Xms8G -Xmx10G -XX:+UseZGC -XX:+UseStringDeduplication -XX:-OmitStackTraceInFastThrow`
- mods 目录含用户全部已验证 mod（**禁止删**）；DH 3.3.3、Iris、Nvidium 0.4.4-beta7-26.3（需 Sodium 0.9.2，当前 0.9.3-alpha 冲突时降级）

## 7. 网络与工具事实
- GitHub 直连超时（HTTP 000，×4）；ghfast.top/gh-proxy.com 镜像 FAIL
- 可通：fabric-maven / maven-central / mojang（piston-meta）/ modrinth（cdn.modrinth.com）/ 华为云·腾讯云 Gradle 镜像
- UTF jar 反编译工具：`...\agents\m_0cwR1yAsk8O\poc\cfr.jar`；反编译输出 `poc\learn\utf_decomp\`
- 26.3 API 查询：`javap -classpath "C:\Users\CHN_W\.gradle\caches\fabric-loom\26.3\minecraft-merged.jar" -p <类名>`
- 关键已读 UTF 文件（utf_decomp 下）：MixinCreateWorldScreen / PresetApplier / PresetPacks / UTFDataGen / Preset / TerrainTab / TerrainPreview / WorldSettings / MixinNoiseBasedChunkGenerator
