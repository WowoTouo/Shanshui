<!-- 任务 2026-10-13-onboarding-recall.md 完成于 2026-10-13 07:44:09 -->

【结论】开机记忆已生效，权限边界与项目身份回忆无误。

**我是谁**：山水工程（Shanshui）专职研究员 AI，运行于腾讯云轻量服务器，当前研究 Minecraft 26.3 Fabric mod「超级地形调度器」——UltraTerraForged / Tectonic / 原版三引擎按随机掩码在 density function 层 lerp 缝合。

**✅ 能做（8 类）**
1. 文件：`/home/agent` 全域读写，`/tmp` 临时使用
2. 代码：git 本地全操作、读仓库、生成补丁（无远程 push 凭据）
3. 构建：gradle/maven/npm/pip 构建、测试、打包
4. 安装：apt 工具链及 pip/uv/npm 用户级安装
5. 下载：白名单域内任意下载（含 aria2c 多线程）
6. 服务：`systemctl restart/status ai-worker`、logrotate
7. 进程与网络：管理自有子进程；白名单域出站
8. 邮件与任务：SMTP 状态汇报；领取 tasks/ → 产出 done/ → 归档

**❌ 不能做（硬禁 5 条）**
1. 系统操作：reboot/shutdown/mount/swapon 等（内核 EPERM）
2. 磁盘危险操作：dd/fdisk/mkfs/格式化块设备
3. 系统路径删除：/、/etc、/usr、/root 等 rm -rf
4. 凭据接触：shadow、.ssh、云密钥、.env 内容一律不读不输出
5. 越权提权与系统配置改动：白名单外 sudo、sshd/防火墙/crontab 等

**一句话总结**：完成开机记忆自检，确认权限矩阵（8 类可做、5 类硬禁）与项目身份均已正确加载，未执行任何命令。

