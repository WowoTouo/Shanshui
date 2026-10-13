<!-- 任务 auto-20261014-003451-Tectonic-final_density-语义取证-输入-输出语义-取值范围.md 完成于 2026-10-14 00:35:18 -->

【结论】现有证据只证明调度器可在 `noise_settings` 层把最终密度函数改写为 `hybrid:final_density`；**不能**据此确认 Tectonic 自有 `final_density` 的输入/输出语义和取值范围，需另查 Tectonic jar/源码。

证据：
- `.../noise_settings/overworld.json:48`：`"function": "hybrid:final_density"`，证明最终密度入口可被数据包替换。
- `.../density_function/final_density.json:6,15`：分别引用 `minecraft:overworld/final_density` 与 `hybrid:vanilla/final_density`，显示缝合/回退结构，但无 Tectonic 标识。
- `ShanshuiPacks.java:75,82`：仅注册这两个 JSON，不包含语义计算。

故“外部调度器能否改写”对噪声设置入口为**能**；Tectonic 的具体语义、值域仍无法验证。

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

