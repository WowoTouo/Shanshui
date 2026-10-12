# Java 环境统一安装 result · 2026-10-13

> 山水工程 Shanshui · 服务器 JDK 27 主 + 25 备用 · 依据总工任务书执行并回报

## 判定（一句话）

**27 构建成功 → 三地统一 27 成立。** 服务器真工程 `gradle build --no-daemon`（Zulu 27）BUILD SUCCESSFUL，GRADLE_EXIT=0；备用 25 未触发，已在位待命。

## 环境清单

| 项 | 值 |
|---|---|
| 主 JDK | Zulu 27.28+101-CA（build 27+35），`/usr/lib/jvm/zulu27` |
| 备用 JDK | Zulu 25.36+205-CA（25.0.4.1 LTS），`/usr/lib/jvm/zulu25` |
| Gradle | 9.8.1（`/opt/gradle-9.8.1`，symlink `/usr/local/bin/gradle`） |
| .env | `JAVA_HOME=/usr/lib/jvm/zulu27` + `JAVA_HOME_ALT=/usr/lib/jvm/zulu25` |
| .env 权限 | `-rw------- agent agent`（600，455 字节，不进 git） |
| 仓库 | `/home/agent/Shanshui`（git bundle 搬运，本地 commit 6f8ecff） |

## java -version 实证

```
主：openjdk version "27" 2026-09-15
    OpenJDK Runtime Environment Zulu27.28+101-CA (build 27+35)
备：openjdk version "25.0.4.1" 2026-08-18 LTS
    OpenJDK Runtime Environment Zulu25.36+205-CA (build 25.0.4.1+1-LTS)
```

agent 用户双 JDK 均实测可用。

## Gradle 构建实测（27，真工程）

- 命令：`export JAVA_HOME=/usr/lib/jvm/zulu27 && cd ~/Shanshui && gradle build --no-daemon`
- 结果：**BUILD SUCCESSFUL in 2m 1s**，5 tasks executed
- 任务链：`compileJava → processResources → classes → processIncludeJars → jar → sourcesJar → assemble → build` 全过；`compileTestJava/test NO-SOURCE`（无测试源码，正常）
- 产物：`build/libs/shanshui-0.1.0.jar`（52K）+ sources jar（37K）
- 字节码实证：12 个 class，major **69 = Java 25**（`options.release = 25` 生效，产物向下兼容）
- Launcher JVM：27（Azul 27+35）
- 全程日志：`/home/agent/logs/build-27.log`（含 java -version 头与完整输出）
- 报错原文：无（未触发 fallback 25 路径）

## sudo 使用范围（不越权核查）

- 唯一提权操作：`apt install -y zulu25-jdk`（zulu27 此前同途径，均在白名单内）
- clone / 构建 / 文件读写全部以 agent 用户身份完成，零额外提权

## 判定口径对照（总工任务书）

| 任务书条款 | 落实 |
|---|---|
| 27 构建成功 → 三地统一 27 | ✅ 成立 |
| build.gradle toolchain=27 + release 25 | ✅ 已改并提交（本地 commit 6f8ecff，服务器 clone 已含） |
| CI 同步 setup-java 25→27 | ⏳ 待 GitHub 仓库地址到位后执行（仓库未建，阻塞中） |
| 27 失败 → 25 备用生效 | 未触发（27 一次通过）；zulu25 已在位，`.env` 的 `JAVA_HOME_ALT` 已记录路径 |

## 安装过程沉淀（复用向）

- Azul apt 源 GPG：`NO_PUBKEY B1998361219BD9C9` → keyserver 抓 key 落 `/etc/apt/keyrings/zulu.gpg` + 源文件补 `signed-by=`
- aria2 大文件多 URI 会被当同一文件镜像：逐个 `-o` + sha256 验证
- 仓库搬运方案（GitHub 未建的过渡期）：本地 `git bundle create --all` → scp → 服务器 agent 用户 `git clone <bundle>`；后续仓库建好后改 remote 即可

## 待办

1. CI：`.github/workflows/build.yml` `setup-java` version 25→27（等仓库地址）
2. 三把钥匙：方舟 API Key + endpoint id ×2（lite/pro）+ GitHub 仓库地址 → 填 `.env` → first-task 闭环
3. 服务器到期 2026-11-12 续费提醒
