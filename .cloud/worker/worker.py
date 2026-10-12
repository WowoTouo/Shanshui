#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
山水工程 AI Worker —— 无人值守连续工作循环
================================================
工作方式：
  1. 轮询 /home/agent/tasks/ 下的 .md 任务文件（一个文件 = 一个任务）
  2. 取最早的任务 → 调方舟豆包 API（OpenAI 兼容）→ AI 产出
  3. 产出存档到 /home/agent/done/<任务名>.result.md，任务原件移入 done/ 归档
  4. 全程写日志 /home/agent/logs/worker.log（logrotate 按天轮转）

设计原则（稳定性）：
  - 无状态：崩了/重启了，任务文件没移走就会重来，天然断点续作
  - 不空转：没任务时 sleep 60，API 失败退避 120s，绝不疯狂重试烧 token
  - 熔断：连续 5 次 API 失败 → 休眠 30 分钟（方舟挂了就别折腾）
  - v1 只做「读任务 → AI 产出文本」；执行权（shell 代码块）留待 CI 兜底后开

任务文件格式（tasks/*.md）：
  ---
  # 任意任务描述正文，AI 会收到全文
  # 建议写清楚：目标、上下文（文件路径）、期望产出格式
"""
import os
import re
import sys
import time
import glob
import shutil
import subprocess
import traceback
from datetime import datetime
from pathlib import Path

BASE = Path('/home/agent')
TASKS_DIR = BASE / 'tasks'
DONE_DIR = BASE / 'done'
LOG_FILE = BASE / 'logs' / 'worker.log'
ENV_FILE = BASE / '.env'
WORK_DIR = BASE / 'work'          # 所有 shell 命令的 cwd 围栏（main() 里创建）

# 方舟（豆包）OpenAI 兼容端点
ARK_BASE_URL = 'https://ark.cn-beijing.volces.com/api/v3'

# ===== 命令黑名单（第三层：命令级兜底）=====
# 前两层（systemd seccomp/capability 沙箱 + sudoers 白名单）是内核级防线，
# 这里是最后一道兜底：宁错杀不放过
FORBIDDEN = [
    # 重启/关机类
    'reboot', 'shutdown', 'halt', 'poweroff', 'init 0', 'init 6', 'kexec',
    'systemctl reboot', 'systemctl poweroff', 'systemctl halt', 'systemctl kexec',
    # 磁盘/分区破坏
    'mkfs', 'fdisk', 'parted', 'dd if=', 'dd of=', 'wipefs', 'shred',
    '> /dev/sd', '> /dev/nvme', '> /dev/vd',
    # fork 炸弹
    ':(){',
    # 用户/权限篡改
    'userdel', 'usermod', 'useradd', 'visudo', 'vipw', 'passwd ',
    'setenforce', 'chmod -r /', 'chown -r /',
    # 递归删除系统级路径（agent 本无权限，双保险）
    'rm -rf /', 'rm -fr /', 'rm -rf /*', 'rm -rf /etc', 'rm -rf /usr',
    'rm -rf /var', 'rm -rf /home', 'rm -rf /boot', 'rm -rf /opt',
    'rm -rf /root', 'rm -rf ~/.ssh', 'rm -rf $home/.ssh',
    # 系统文件写入（/etc /usr /boot /sys /proc /root /ubuntu家目录）
    '> /etc', '>> /etc', '> /usr', '>> /usr', '> /boot', '> /sys', '> /proc',
    '> /root', '> /home/ubuntu', '>> /home/ubuntu', 'tee /etc', 'tee -a /etc',
    # 防火墙/网络层
    'iptables', 'nftables', 'ufw ', 'firewall-cld', 'firewall-cmd',
    # SSH 密钥/持久化篡改
    'ssh-keygen', '> ~/.ssh', '>> ~/.ssh', '> /home/', '>> /home/',
    'crontab -r', 'crontab -e',
    # 服务层破坏
    'systemctl mask', 'systemctl disable ssh', 'systemctl stop ssh',
    'systemctl restart ssh', 'systemctl restart sshd',
    # 内核模块/挂载
    'swapon', 'swapoff', 'mount ', 'umount ', 'insmod', 'modprobe', 'rmmod',
    # 包删除（只允许 install，删除走人工）
    'apt-get remove', 'apt remove', 'apt-get purge', 'apt purge',
    'dpkg -r', 'dpkg --remove', 'dpkg -p', 'apt autoremove',
    # 进程屠杀
    'kill -9 1', 'killall', 'pkill -9',
    # 日志抹除
    'history -c', 'rm -rf /var/log', '> /var/log',
    # 凭据读取/回显（2026-10-13 总工提醒：凭据资产保护，与系统目录写入同级）
    '/home/agent/.env', '~/.env', '$home/.env', 'cat .env', 'msmtprc', '.tccli',
    'printenv', 'export -p', 'declare -p',
    '/proc/self/environ', '/proc/*/environ',
]

# ===== token 分级调度（2026-10-13 总工指令）=====
# 任务文件头部写 `model: lite` 用轻量模型（跑腿/日志/机械劳动），
# 不写或 `model: pro` 用旗舰（地形数学/源码分析/方案设计）。
# 注意：方舟实际调用用「推理接入点 endpoint id」（控制台创建，形如 ep-xxxx），
# 钥匙到位后把下面两个值换成你的接入点 id。
def _build_model_map():
    """模型分级映射。方舟实际调用用「推理接入点 endpoint id」（ep-xxxx），
    经 .env 的 ARK_MODEL_LITE / ARK_MODEL_PRO 注入（旧键 ARK_MODEL 兼容）。"""
    return {
        'lite': os.environ.get('ARK_MODEL_LITE', 'doubao-lite-32k'),
        # ARK_MODEL_PRO 优先（2026-10-13 钥匙到位，总工给的命名），兼容旧键 ARK_MODEL
        'pro': os.environ.get('ARK_MODEL_PRO') or os.environ.get('ARK_MODEL', 'doubao-pro-32k'),
    }


# import 期快照：此刻 .env 尚未加载，仅供测试与默认值；
# load_env() 跑完后会刷新为 .env 真实值（见 load_env 末尾，2026-10-13 404 踩坑修复）
MODEL_MAP = _build_model_map()

# ===== 凭据保护（2026-10-13 总工提醒：SMTP 凭据与 tccli 密钥同等对待）=====
# .env 中这些键的值视为敏感资产：AI 任务可读（调用需要），但绝不回显到
# 日志 / 结果文件 / 命令输出。redact() 在所有出口做确定性打码——
# 第四层防线，不依赖 AI 纪律（AI 违纪也漏不出去）。
SENSITIVE_KEYS = ('ARK_API_KEY', 'GITHUB_TOKEN', 'MAIL_PASS', 'FEISHU_WEBHOOK')
SECRETS: list[str] = []


def redact(text: str) -> str:
    """出口脱敏：.env 敏感键的值一律替换为 ***"""
    if not text or not SECRETS:
        return text
    for s in SECRETS:
        text = text.replace(s, '***')
    return text


def strip_think_tags(text: str) -> str:
    """剥离方舟 seed 系模型原样回传的思考块（<seed:think_xxx>...</think_xxx>）——
    思考内容不进执行提取与结果文件（2026-10-13 实测：端点把思考块混在 content 里，
    且思考块内的示例命令有被 extract_shell_blocks 误提取执行的风险）"""
    return re.sub(r'<seed:think_[^>]*>.*?</think_[^>]*>', '', text, flags=re.DOTALL).strip()

SYSTEM_PROMPT = """你是「山水工程 Shanshui」项目的专职 AI 代理，7×24 无人值守运行。

【项目背景】
Minecraft 1.20.2 Fabric mod「山水工程·超级地形调度器」：UltraTerraForged + Tectonic + 原版三个地形引擎按随机掩码分区共存，density function 层 lerp(mask, A, B) 缝合。技术栈 MC 26.3 预去混淆 + Fabric Loom + Gradle + JDK 25。

【铁律（不可违背）】
1. 只做任务里指派的事，不自行扩展 scope，不「顺手优化」
2. 不改架构、不重构——发现架构问题写进结论报告，绝不动手改
3. 服务器上的代码仓库对你只读：你做研究和分析，不改代码
4. 产出结论优先落仓库 docs/ 目录（git commit + push），任务结果文件同步存档
5. 重大变更先出方案等人审，绝不直接执行
6. 凭据保护：严禁读取或输出 ~/.env、.msmtprc、~/.tccli 等凭据文件，严禁在命令或产出中书写 API Key/授权码/token 明文——系统对所有出口自动打码兜底，但触发即违纪

【能力与边界】
- 你回复中的 ```bash 代码块会被系统自动提取执行（cwd 固定在 ~/work/，输出回写结果文件）
- 受控 root 白名单：`sudo apt-get install <包>`、`sudo systemctl restart ai-worker`；删除类命令一律不可用，别试
- 系统目录（/etc /usr 等）不可写，不要尝试提权

【风格】
简体中文、结构化、硬核直球；不确定就明确说不确定，宁可少做不可做错。每个任务结束时用一句话总结「做了什么 + 结论如何」。"""


def log(msg: str):
    line = f'[{datetime.now():%Y-%m-%d %H:%M:%S}] {redact(msg)}\n'
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(line)


def load_env():
    """从 ~/.env 读密钥（600 权限，永不进 git）；敏感键值收集进 SECRETS 供出口脱敏"""
    global SECRETS, MODEL_MAP
    if not ENV_FILE.exists():
        return
    for raw in ENV_FILE.read_text(encoding='utf-8').splitlines():
        line = raw.strip()
        if line and not line.startswith('#') and '=' in line:
            k, v = line.split('=', 1)
            k, v = k.strip(), v.strip()
            os.environ[k] = v
            if k in SENSITIVE_KEYS and len(v) >= 8:
                SECRETS.append(v)
    # 刷新模型映射：import 时 .env 未加载，MODEL_MAP 冻结在默认值——
    # 不刷新就会拿 doubao-pro-32k 默认名去调方舟报 404（2026-10-13 实测踩坑）
    MODEL_MAP = _build_model_map()


def get_client():
    """延迟导入：密钥没配好时 worker 也能起来空转等任务"""
    from openai import OpenAI
    api_key = os.environ.get('ARK_API_KEY', '').strip()
    if not api_key:
        return None
    return OpenAI(base_url=ARK_BASE_URL, api_key=api_key)


def extract_shell_blocks(reply: str) -> list[str]:
    """从 AI 回复中提取 bash/shell 代码块（要执行的命令）"""
    blocks = re.findall(r'```(?:bash|shell|sh)\s*\n(.*?)```', reply, re.DOTALL)
    return [b.strip() for b in blocks if b.strip()]


def execute_shell(cmd: str) -> tuple[bool, str]:
    """第三层防线：黑名单 → 资源围栏 → 隔离执行 → 输出截断"""
    low = cmd.lower()
    for p in FORBIDDEN:
        if p in low:
            return False, f'BLOCKED（命中黑名单: {p}）'
    wrapped = f'ulimit -t 300; ulimit -f 1048576; ulimit -u 256; {cmd}'
    try:
        # bash -c 而非 shell=True：shell=True 用 /bin/sh（dash），不支持 ulimit -u
        # （2026-10-13 实测报 Illegal option -u，进程数限制形同虚设）
        r = subprocess.run(
            ['bash', '-c', wrapped], capture_output=True, text=True,
            timeout=320, cwd=str(WORK_DIR),
        )
        out = (r.stdout + r.stderr).strip()[-4000:]
        return r.returncode == 0, redact(out) or '(无输出)'
    except subprocess.TimeoutExpired:
        return False, 'TIMEOUT（320s 已终止）'


def detect_model(content: str) -> str:
    """任务头部 `model: lite/pro` 分级调度，缺省 pro"""
    m = re.search(r'^model:\s*(\w+)', content, re.MULTILINE)
    if m and m.group(1).lower() in MODEL_MAP:
        return MODEL_MAP[m.group(1).lower()]
    return MODEL_MAP['pro']


def chat_completions_stream(client, model: str, messages: list) -> tuple[str, object]:
    """流式调用方舟（v3.4）：迭代聚合 chunk，返回 (聚合全文, usage|None)。
    - stream=True 首 token 更快；**错误在迭代中途抛出**——本函数不吞，异常上抛，
      由 main() 主循环的 try/except 记录 ERROR 并按退避/熔断策略处理
    - usage 只在最后 chunk 顶层可能携带；方舟不返回则 None，
      调用方日志记 '?'（省略，不报错）
    """
    content = ''
    usage = None
    stream = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.3,
        max_tokens=4096,
        stream=True,
    )
    for chunk in stream:
        if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
            content += chunk.choices[0].delta.content
        if getattr(chunk, 'usage', None):
            usage = chunk.usage
    return content, usage


def process_task(client, task_path: Path):
    name = task_path.name
    content = task_path.read_text(encoding='utf-8')
    log(f'TASK START  {name} ({len(content)} chars)')

    model = detect_model(content)
    log(f'TASK MODEL  {name} -> {model}')
    reply, usage = chat_completions_stream(client, model, [
        {'role': 'system', 'content': SYSTEM_PROMPT},
        {'role': 'user', 'content': content},
    ])
    reply = redact(reply)   # 出口脱敏：AI 回复先过打码，再进执行/落盘流程
    reply = strip_think_tags(reply)   # v3.3：剥离思考块，防伪命令进执行提取（聚合后执行，顺序不变）
    tokens = getattr(usage, 'total_tokens', None) if usage else None
    log(f'TASK LLM OK  {name} | model={model} tokens={tokens if tokens else "?"}')

    # ===== 执行权 v2：提取并执行 shell 块 =====
    blocks = extract_shell_blocks(reply)
    exec_log = ''
    if blocks:
        log(f'TASK EXEC   {name} 提取到 {len(blocks)} 个命令块')
        parts = ['\n\n---\n## 执行记录（worker 自动执行）\n']
        for i, cmd in enumerate(blocks, 1):
            ok, out = execute_shell(cmd)
            parts.append(f'### 命令 {i}\n```bash\n{cmd[:500]}\n```\n**{"成功" if ok else "失败/拒绝"}**\n```\n{out}\n```\n')
            log(f'TASK EXEC   {name} cmd#{i} ok={ok}')
        exec_log = '\n'.join(parts)

    DONE_DIR.mkdir(exist_ok=True)
    result_path = DONE_DIR / f'{name}.result.md'
    result_path.write_text(
        redact(
            f'<!-- 任务 {name} 完成于 {datetime.now():%Y-%m-%d %H:%M:%S} -->\n\n{reply}\n{exec_log}\n'
        ),
        encoding='utf-8',
    )
    shutil.move(str(task_path), str(DONE_DIR / name))
    log(f'TASK DONE    {name} -> done/{name}.result.md')


def main():
    TASKS_DIR.mkdir(exist_ok=True)
    DONE_DIR.mkdir(exist_ok=True)
    WORK_DIR.mkdir(exist_ok=True)
    load_env()

    if not os.environ.get('ARK_API_KEY'):
        log('WARN: ARK_API_KEY 未配置，worker 空转等待（填好 ~/.env 后自动生效）')

    fail_streak = 0
    while True:
        try:
            client = get_client()
            # 排除 README.md：任务目录的说明文件不是任务（2026-10-13 修复）
            tasks = sorted(
                p for p in glob.glob(str(TASKS_DIR / '*.md'))
                if Path(p).name.lower() != 'readme.md'
            )

            if not client:
                # 没钥匙：安静等，不烧任何东西
                time.sleep(60)
                continue

            if not tasks:
                time.sleep(60)
                continue

            task_path = Path(tasks[0])
            try:
                process_task(client, task_path)
                fail_streak = 0
            except Exception as e:
                fail_streak += 1
                log(f'ERROR {task_path.name}: {type(e).__name__}: {e}')
                if fail_streak >= 5:
                    log('CIRCUIT BREAK: 连续 5 次失败，休眠 30 分钟')
                    time.sleep(1800)
                    fail_streak = 0
                else:
                    time.sleep(120)
        except Exception:
            # 主循环本身的意外也不许退出
            log(f'FATAL(main loop): {traceback.format_exc()}')
            time.sleep(120)


if __name__ == '__main__':
    log('=== worker process start ===')
    main()
