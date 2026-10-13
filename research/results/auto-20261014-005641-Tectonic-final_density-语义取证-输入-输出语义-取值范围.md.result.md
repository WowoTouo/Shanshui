<!-- 任务 auto-20261014-005641-Tectonic-final_density-语义取证-输入-输出语义-取值范围.md 完成于 2026-10-14 00:58:08 -->

【结论】现有证据仅能证明：调度器可在噪声设置层把世界最终密度入口替换为 `hybrid:final_density`，并以数据包 DF 组合原版最终密度；**不能证明 Tectonic `final_density` 自身的输入/输出语义、取值范围，亦不能证明其内部节点可被外部改写**，该部分仍须反编译 Tectonic jar 取证。

证据：
- `src/main/resources/templates/.../noise_settings/overworld.json:48`：`"function": "hybrid:final_density"`，证明最终密度入口可被数据包指向自定义 DF。
- `.../density_function/final_density.json:6` 引用 `minecraft:overworld/final_density`；同文件 `:15` 引用 `hybrid:vanilla/final_density`，证明当前方案是 DF 层组合/缝合。
- `src/main/java/com/shanshui/data/ShanshuiPacks.java:75,82` 将上述两个 `final_density.json` 写入生成包。
- 其余命中均为 `gradlew`、shell、`.env.template`，与 Tectonic 语义无关，不能作为取值范围或可改写性证据。

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

