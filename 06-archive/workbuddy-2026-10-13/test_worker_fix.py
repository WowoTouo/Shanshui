import importlib.util
P = "D:/JAVA21orPython/AI/2026-10-13-01-06-24/worker-deployed.py"
spec = importlib.util.spec_from_file_location("w", P)
w = importlib.util.module_from_spec(spec)
spec.loader.exec_module(w)   # import 成功即语法 OK

def check(name, cond):
    print(("PASS " if cond else "FAIL ") + name)

# T1 整段思考块 -> 回退抽取内文（空结果修复核心）
r1 = w.strip_think_tags("<seed:think_abc>这是模型完整答案</think_abc>")
check("T1 all-think 回退非空", bool(r1.strip()) and "完整答案" in r1)

# T2 混合：思考块被剥、正文保留
r2 = w.strip_think_tags("前置<seed:think_x>内部思考</think_x>后置结论")
check("T2 mixed 剥思考留正文", "前置" in r2 and "后置" in r2 and "思考" not in r2)

# T3 无思考块：原样
r3 = w.strip_think_tags("普通回复")
check("T3 normal 原样", r3 == "普通回复")

# T4 STALL 常量
check("T4 STALL_RETRY_AFTER==6", w.STALL_RETRY_AFTER == 6)

# T5 最终兜底逻辑复现：剥后为空 -> 占位（模拟 process_task 尾部）
final = w.strip_think_tags("<seed:think_z> </think_z>")
placeholder = ("【worker 兜底】模型回复经思考块/草稿区/tool_call 剥离后为空。"
               "可能形态：整段思考块 / 纯空白 / 纯 tool_call 垃圾。")
guard = final if final.strip() else placeholder
check("T5 空则占位非空", bool(guard.strip()))

# T6 draft 协议不受影响
f, d = w.strip_draft("正文<draft>草稿内容</draft>")
check("T6 draft 剥离", "正文" in f and "草稿内容" in d and "draft" not in f)

print("DONE")
