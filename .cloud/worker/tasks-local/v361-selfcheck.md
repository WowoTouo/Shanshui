# 自检任务：tool_call 执行验证
model: pro
## 目标
执行 bash 命令：echo V361_EXEC_OK && date
## 要求
把所有命令写在 bash 代码块中（系统会自动提取执行）。
## 期望产出
把命令输出贴进 result。