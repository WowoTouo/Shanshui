# DLC-007 · Deep Thinking On-Demand Protocol
> DLC = Skill extension card. Defines when and how to dynamically enable deep thinking mode for stuck problems.
> Mount: worker.py loads `/home/agent/dlc/*.md` (sorted by filename) into system prompt at startup.
> Version: v1.0 · 2026-10-14
---
## 1. Default: Deep Thinking OFF
- All routine tasks run with deep thinking DISABLED to conserve tokens.
- Deep thinking consumes significantly more tokens per call — use only when necessary.

## 2. Trigger Conditions (Watchdog Auto-Detect)
The timeout watchdog checks every 10 minutes. Deep thinking is triggered when:
- Same task has been retried ≥3 times with zero effective output (STALL loop detected)
- OR a task has been stuck for >60 minutes without completion
- OR supervisor AI explicitly requests deep thinking in its assessment

## 3. How Each AI Enables Deep Thinking

### Main AI (Shanshui / Doubao-Seed-Evolving)
- This model does NOT support a native `thinking` parameter.
- Workaround: when deep thinking is needed, prepend this prefix to the task prompt:
  `[DEEP THINKING MODE] Take extra time to reason through this problem step by step. Before outputting any code or conclusion, first analyze the root cause, then propose a solution, then verify it against constraints.`
- This simulates deep thinking via prompt engineering at minimal extra token cost.

### Supervisor AI (DeepSeek V4.1 Flash)
- This model supports the `thinking` parameter via Ark SDK.
- Enable with: `thinking={"type": "enabled"}`, timeout=1800
- Use only when watchdog detects a persistent STALL loop that the main AI cannot resolve.

### Backup AI (DeepSeek V4 Pro)
- This model supports the `thinking` parameter via Ark SDK.
- Enable with: `thinking={"type": "enabled"}`, timeout=1800
- Use for complex verification tasks that require deep reasoning.

## 4. Watchdog Integration
When the timeout watchdog detects a persistent STALL loop (same task retried ≥3 times with zero progress):
1. Log: `[WATCHDOG] Deep thinking triggered for <task_name>`
2. If main AI is stuck: prepend deep thinking prefix to the next task spawn
3. If supervisor assessment is needed: call supervisor with thinking=enabled
4. After deep thinking resolves the issue, revert to normal mode

## 5. Token Economy
- Deep thinking is OFF by default — zero extra cost for normal operation
- Triggered only by watchdog on detected STALL (rare)
- Each deep thinking call costs ~2-3x normal tokens — use sparingly
- Max 3 deep thinking calls per day to prevent quota exhaustion

## 6. Project Name
- The project is officially named **山水工程 / Shanshui** (matching the repository name)
- All references to "TBPRO" in legacy files are aliases for the same project
- New files and communications should use 山水工程 or Shanshui
