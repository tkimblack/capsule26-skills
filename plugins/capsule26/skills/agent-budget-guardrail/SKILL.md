---
name: agent-budget-guardrail
description: A minimal circuit breaker that logs autonomous-agent spend and automatically returns HALT once a budget threshold is crossed (balance percentage, daily cap, or session cap). Call it before any action that costs money.
license: MIT
---

# Agent Budget Guardrail

A minimal guardrail that stops an autonomous AI agent from spending its whole
budget without noticing. Not a prompting trick — it's code that persists state
and makes the call from outside the agent.

## When to use it

- **Before** any action that costs money (API call, paid tool, purchase): call
  `check_budget()` first.
- At the start of a session, to see how much this session is allowed to spend.
- After an action completes, call `record_spend()` with the real cost.

## Setup

```bash
cd scripts
cp config.example.json config.json
# edit initial_balance / daily_limit / session_limit / halt_threshold_pct
```

## Usage

```bash
# Check current budget state (always before a costly action)
python3 budget_guardrail.py check

# Record actual spend (after the action completes)
python3 budget_guardrail.py spend 0.42 "summarization task with gpt-4o"

# See recent spend log
python3 budget_guardrail.py log
```

If `check`'s output has `status: HALT`, the agent should stop taking any
further costly action and wait for a human to look.

```json
{
  "status": "OK",
  "balance": 42.10,
  "balance_pct_remaining": 84.2,
  "daily_spend_7d_avg": 0.38,
  "session_spend": 0.0,
  "reason": null
}
```

`HALT` triggers on any one of:

1. Balance dropped below `initial_balance * halt_threshold_pct`
2. 7-day rolling average daily spend exceeds `daily_limit`
3. This session's cumulative spend exceeds `session_limit`

## Design principles

- **Decide from recorded facts, not self-reports.** The log
  (`spend_log.jsonl`) is append-only; the judgment logic only ever looks at
  aggregates of that log.
- **Fail closed.** If any condition matches, HALT regardless of reason.
  Resuming requires a human to reset config.json.
- This is the minimal implementation of "cost control" alone. Failure handling
  (idempotency, staged permissions), classifying which actions need approval,
  and a full integration guide with this agent's own real numbers are in the
  paid **agentkeeper** package ($1):
  → https://capsule26.com/go?k=us-agentkeeper&u=https%3A%2F%2Ftkimblack.gumroad.com%2Fl%2Fagentkeeper-us&r=repo

## License

MIT
