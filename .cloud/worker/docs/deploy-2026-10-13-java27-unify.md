# Java 环境三地统一 27 · 部署与验证报告

> 山水工程 Shanshui · 2026-10-13 · 依据总工落地清单执行

## 一、结论（验收态）

- ✅ **服务器 Java 环境配置完毕**：Zulu 27.28+101-CA（build 27+35），`/usr/lib/jvm/zulu27` 符号链接与指定路径一致，agent 用户可用
- ✅ **咽喉实测解除**：Gradle 9.8.1 跑 JDK 27 全过（服务器最小工程 + 本地真实工程双实证）
- ✅ **本地 build.gradle 已改并验证**：toolchain 27 + `options.release = 25`，javaw 静默编译 BUILD SUCCESSFUL，字节码 major 69 = Java 25
- ⏳ **CI 待办**：`setup-java` version 25→27——阻塞中（GitHub 仓库地址未到，仓库未建）
- 📌 **备用方案在位**：27 研究过程不可用 → 服务器 `apt install zulu25-jdk`；本地旧 JDK 25 保留未删

## 二、服务器侧安装链（按总工给的成功配方）

1. `wget zulu-repo_1.0.0-3_all.deb` → `dpkg -i` 建 Azul apt 源
2. `apt update` 报 `NO_PUBKEY B1998361219BD9C9`（deb 源文件缺 `signed-by=`）
   - 修复：keyserver 抓 GPG key → `/etc/apt/keyrings/zulu.gpg` + 源文件 sed 补 `signed-by=`
3. `apt install -y zulu27-jdk` → 元包链 `zulu27-jdk → zulu27-ca-jdk → zulu27-ca-jdk-headless → zulu27-ca-jre-headless`
4. 验证：`java -version` = Zulu27.28+101-CA 27+35，javac 27，`/usr/lib/jvm/zulu27 → zulu27-ca-amd64` 符号链接正确

**aria2 大文件坑（已解决）**：多 URI 被当同一文件镜像下载，只下 87MiB 且文件名错盖 → sha256 验证实为 jdk-headless 内容 → mv 改名 + 单独重下 jre-headless（f63fd3ea… 验证通过）。教训：镜像场景逐个 `-o` + `--checksum=sha-256=`。

## 三、Gradle 咽喉实测（统一 27 的前置未知数）

**结论：Gradle 9.8.1 官方支持 Java 27**（发布亮点第一条 "Java 27 support"），无需升级 Gradle。

| 实证点 | 服务器 | 本地 |
|---|---|---|
| Launcher JVM | 27（Azul 27+35） | 27（Zulu27.28+101-CA） |
| 工程 | 最小工程 toolchain 27 + release 25 | Shanshui 真实工程（Loom 1.19.0-alpha.2） |
| 结果 | BUILD SUCCESSFUL | BUILD SUCCESSFUL in 14s，exit 0 |
| 字节码 | major 69 = Java 25 | major 69 = Java 25（12 个 class 全量） |
| 运行 | hello from java 27 正常 | compileJava 无警告无异常 |

- `--release 25` 在 JDK 27 下产出 major 69 字节码 → 可跑 Java 25+ 运行时，MC 运行时/玩家侧零影响
- 注：major 69 = Java 25（65 = Java 21），此前命令注释口误已纠正

## 四、本地侧改动清单

- `build.gradle`：
  - `java { toolchain { languageVersion = JavaLanguageVersion.of(27) } }`（原 of(25)，带注释）
  - `tasks.withType(JavaCompile).configureEach { it.options.release = 25 }`（带注释）
- 本地 Zulu 27：`C:\Program Files\Zulu\zulu-27`（与服务器同 build 27+35）
- wrapper：9.8.1（腾讯云镜像 `gradle-9.8.1-bin.zip`）未动
- 验证方式：`javaw -jar gradle/wrapper/gradle-wrapper.jar compileJava --no-daemon --console=plain` + 重定向（遵循无窗口化纪律，全程零弹窗）

## 五、服务器 .env 追加

```
JAVA_HOME=/usr/lib/jvm/zulu27
```

权限 600 agent，不进 git（凭据资产同款待遇）。

## 六、未决项

1. **CI**：`.github/workflows/build.yml` 的 `setup-java` version 25→27——等 GitHub 仓库地址到位后一并做
2. **三把钥匙**（AI Worker 开工前置）：方舟 API Key + endpoint id ×2（lite/pro）+ GitHub 仓库地址 → 填 `/home/agent/.env` → 重启 ai-worker → first-task 闭环
3. **服务器到期**：2026-11-12（包年包月）

## 七、安装经验沉淀（复用向）

- Azul deb 源无 `signed-by=` → keyserver 抓 key 落 keyrings + 源文件补字段
- aria2 多 URI 镜像陷阱：逐文件 `-o` + sha256 验证
- Gradle toolchain 自动探测：`C:\Program Files\Zulu\` 标准路径无需额外配置即被识别
