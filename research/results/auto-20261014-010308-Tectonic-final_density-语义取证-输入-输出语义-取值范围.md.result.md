<!-- 任务 auto-20261014-010308-Tectonic-final_density-语义取证-输入-输出语义-取值范围.md 完成于 2026-10-14 01:03:33 -->

【结论】现有证据**不能取证 Tectonic `final_density` 的输入/输出语义与取值范围**：检索命中的均为本项目调度器模板，未命中 Tectonic 源码或其数据包定义。可确认的是，外部调度器能够在 `noise_settings` 层把最终密度函数替换为自定义 `hybrid:final_density`，并在其中包装/插值原版最终密度；但能否同样改写 Tectonic，仍须补查 Tectonic 的 df 文件与注册名。

证据：
- `src/main/resources/templates/zz_hybrid_scheduler/data/minecraft/worldgen/noise_settings/overworld.json:48`：`"function": "hybrid:final_density"`，证明世界生成最终入口已被替换。
- `.../density_function/final_density.json:6`：右输入引用 `"minecraft:overworld/final_density"`。
- 同文件 `:15`：右输入引用 `"hybrid:vanilla/final_density"`。
- `src/main/java/com/shanshui/data/ShanshuiPacks.java:75,82`：上述 df 文件由 mod 打包进数据包。

下一步应反编译/解包 Tectonic jar，检索 `worldgen/density_function/**/final_density.json` 及其被 `noise_settings` 引用位置。

---
（据 worker 确定性侦察取证合成，检索命中见下）
/home/agent/Shanshui/.env.template:7:ARK_MODEL_LITE=doubao-seed-evolving-xxx   # 轻量模型 endpoint
/home/agent/Shanshui/gitpush.sh:1:#!/bin/bash
/home/agent/Shanshui/gradlew:27:#   (1) You need a POSIX-compliant shell to run this script. If your /bin/sh is
/home/agent/Shanshui/gradlew:28:#       noncompliant, but you have some other compliant shell such as ksh or
/home/agent/Shanshui/gradlew:29:#       bash, then to run this script, type that shell name before the whole
/home/agent/Shanshui/gradlew:34:#       Busybox and similar reduced shells will NOT work, because this script
/home/agent/Shanshui/gradlew:35:#       requires all of these POSIX shell features:
/home/agent/Shanshui/gradlew:44:#   (2) This script targets any POSIX shell, so it avoids extensions provided
/home/agent/Shanshui/gradlew:86:# shellcheck disable=SC2034
/home/agent/Shanshui/gradlew:149:        # shellcheck disable=SC2039,SC3045
/home/agent/Shanshui/gradlew:157:        # shellcheck disable=SC2039,SC3045
/home/agent/Shanshui/gradlew:206:#   * DEFAULT_JVM_OPTS, JAVA_OPTS, and optsEnvironmentVar are not allowed to contain shell fragments,
/home/agent/Shanshui/gradlew:207:#     and any embedded shellness will be escaped.
/home/agent/Shanshui/gradlew:231:# but POSIX shell has neither arrays nor command substitution, so instead we
/home/agent/Shanshui/gradlew:233:# character that might be a shell metacharacter, then use eval to reverse
/home/agent/Shanshui/src/main/java/com/shanshui/data/ShanshuiPacks.java:75:                "data/hybrid/worldgen/density_function/final_density.json",
/home/agent/Shanshui/src/main/java/com/shanshui/data/ShanshuiPacks.java:82:                "data/hybrid/worldgen/density_function/vanilla/final_density.json",
/home/agent/Shanshui/src/main/resources/templates/zz_hybrid_scheduler/data/hybrid/worldgen/density_function/final_density.json:6:    "right": "minecraft:overworld/final_density"
/home/agent/Shanshui/src/main/resources/templates/zz_hybrid_scheduler/data/hybrid/worldgen/density_function/final_density.json:15:    "right": "hybrid:vanilla/final_density"
/home/agent/Shanshui/src/main/resources/templates/zz_hybrid_scheduler/data/minecraft/worldgen/noise_settings/overworld.json:48:      "function": "hybrid:final_density",

