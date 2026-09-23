---
name: agent-retry-safety
description: A lightweight tool that decides whether an autonomous agent's failed action is safe to retry, based on the nature of its side effects (safe_retry / dedupe_required / unsafe_retry). Prevents double-charging or double-sending. Callable from Claude Code error handling or your own harness's retry loop.
license: MIT
---

# agent-retry-safety

When an autonomous agent's API call or tool execution fails, "just retry it"
is dangerous. Unconditionally retrying actions with accumulating side
effects — double-charging a payment, double-sending an email, creating
duplicate orders — can cause irreversible damage.

This skill **matches an action name against three classes and mechanically
decides whether a retry is safe**.

## What it does

- Matches an action name (wildcard `*` supported) against patterns, sorting into:
  - `safe_retry`: read-only/idempotent actions — result doesn't change on
    repeat, always safe to retry
  - `dedupe_required`: payments, order creation — safe to retry *if* the same
    idempotency key is supplied
  - `unsafe_retry`: sending email, deletes, transfers — needs human
    confirmation before retrying
- Returns `SAFE_RETRY` / `DEDUPE_REQUIRED` / `UNSAFE_RETRY` and an exit code (0/2/1)
- Unknown actions default to `unsafe_retry` (fail-safe: unknowns get stopped)
- Appends every decision to a JSONL log

## Usage

```bash
python3 scripts/retry_safety.py --config scripts/config.example.json --action "get_status"
# => SAFE_RETRY: read-only/idempotent action, retry is always safe (exit code 0)

python3 scripts/retry_safety.py --config scripts/config.example.json --action "charge_payment"
# => DEDUPE_REQUIRED: ... supply one before retrying (exit code 2)

python3 scripts/retry_safety.py --config scripts/config.example.json --action "charge_payment" --idempotency-key "abc123"
# => SAFE_RETRY: dedupe_required action but idempotency-key present (abc123) (exit code 0)

python3 scripts/retry_safety.py --config scripts/config.example.json --action "send_email"
# => UNSAFE_RETRY: ... human confirmation required before retry (exit code 1)
```

Exit code convention: `0=SAFE_RETRY` / `1=UNSAFE_RETRY` / `2=DEDUPE_REQUIRED`.
Branch directly in a shell retry loop: `case $? in 0) retry;; 2) needs_key;; *) ask_human;; esac`.

## Config (config.example.json)

```json
{
  "safe_retry": ["get_*", "list_*", "read_*", "check_*"],
  "dedupe_required": ["create_order*", "charge_payment*", "submit_form*"],
  "unsafe_retry": ["send_email*", "send_payment*", "delete_*", "transfer_funds*"],
  "default": "unsafe_retry"
}
```

Zero dependencies, standard library only.

## Beyond this skill (the paid package)

This is the minimal classifier for "which actions are retry-safe". In
practice you also need:
- Retry count limits and backoff design (how many times, what interval)
- How the agent itself issues and stores idempotency keys
- Full error-handling design combining this with approval-gate decisions
- A token-cost checklist specific to Claude Code / Agent Skills

All of that, plus this agent's own real numbers, is in the paid **agentkeeper**
package ($1):
→ https://capsule26.com/go?k=us-agentkeeper&u=https%3A%2F%2Ftkimblack.gumroad.com%2Fl%2Fagentkeeper-us&r=repo

## License

MIT. Modify and embed freely.
