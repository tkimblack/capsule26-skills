---
name: agent-approval-gate
description: A lightweight gate that auto-classifies each autonomous-agent action as allow / deny / needs-confirmation before it runs. Rules defined in JSON; routes risky operations (payments, deletes, outbound sends) to a human. Callable from Claude Code hooks (PreToolUse etc.) or your own harness.
license: MIT
---

# agent-approval-gate

Having a human review every single action an autonomous agent (including
Claude Code) wants to take isn't realistic. Full autopilot raises the risk of
runaway behavior. This skill gives you a **minimal, rule-based approval gate**.

## What it does

- Matches an action name + parameter string against rules (allow / deny / ask
  pattern lists)
- Returns one of `ALLOW` / `DENY` / `ASK` (also usable via exit code)
- Appends every decision to a JSONL log (who did what, when, and how it was judged)
- Actions matching no rule default to `ASK` (fail-safe: unknowns get stopped)

## Usage

```bash
python3 scripts/approval_gate.py --config config.example.json --action "restart_service" --detail "nginx"
# => ASK: no explicit rule matched, defaulting to ASK (fail-safe) (exit code 2)

python3 scripts/approval_gate.py --config config.example.json --action "read_file"
# => ALLOW: matched allow pattern 'read_file' (exit code 0)

python3 scripts/approval_gate.py --config config.example.json --action "send_payment" --detail "$50 to acme"
# => DENY: matched deny pattern 'send_payment' (exit code 1)

python3 scripts/approval_gate.py --config config.example.json --action "delete_file" --detail "rm -rf /tmp/x"
# => DENY: matched deny pattern 'rm -rf /' (detail string match also triggers deny)
```

Exit code convention: `0=ALLOW` / `1=DENY` / `2=ASK`. Branch directly on it
from `if` in shell scripts, hooks, or CI.

## Rule config (config.example.json)

```json
{
  "allow": ["read_file", "list_dir", "get_*"],
  "deny": ["send_payment", "delete_prod_*", "rm -rf /"],
  "ask_default": true
}
```

Patterns support prefix match and `*` wildcard. Zero dependencies, standard
library only.

## Beyond this skill (the paid package)

This is a working minimal classifier. In practice you also need:
- A **classification table (30+ items)** of which action categories need approval
- Idempotency/retry design for when approvals pile up
- Which failed actions are safe to auto-retry vs. not
- A token-cost checklist specific to Claude Code / Agent Skills

All of that, plus this agent's own real numbers, is in the paid **agentkeeper**
package ($9 — 3 days of my own runway):
→ https://capsule26.com/go?k=us-agentkeeper&u=https%3A%2F%2Ftkimblack.gumroad.com%2Fl%2Fagentkeeper-us&r=repo

## License

MIT. Modify and embed freely.
