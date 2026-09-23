---
name: agentkeeper
description: A design pattern for letting code outside the agent's reach enforce balance, tier, session budget and policy violations for an autonomous AI agent. Append-only ledger, a runway-based tier system that degrades as money runs low, and a session-budget circuit breaker — dependency-free Python.
license: MIT
---

# agentkeeper

This is the design pattern pulled out of the harness actually running
https://capsule26.com/live — an autonomous AI agent that stops when its balance
hits zero. Instead of "asking the agent nicely to behave", this enforces budget
and policy in **a layer the agent physically cannot touch**.

## Three pillars

### 1. Append-only ledger (with duplicate-charge protection)
Spend and income are recorded in SQLite; `UPDATE`/`DELETE` are forbidden by SQL
triggers. Income is only recorded when there's a payment-provider transaction ID
(`ref`), and **duplicate `ref`s raise** — safe against webhook replays, retried
requests, or an agent self-reporting a fake sale. (A recent audit of 110 AI
usage-tracking tools found double-charging on already-paid rows as one of the
most common billing bugs — this is the guard against exactly that class of bug.)

```python
# the idea, sketch only (full implementation in the paid package)
def balance(self) -> float:
    return self._sum("fund") + self._sum("income") - self._sum("refund") - self._sum("inference")
```

### 2. A tier system that degrades with runway
`balance / 7-day average daily spend = runway days`. Model choice, session count,
and whether new ventures are even allowed all shrink as runway shortens.

```python
def tier_for(balance: float, runway_days: float) -> str:
    if balance <= 0: return "dead"
    if runway_days > 90: return "normal"
    if runway_days >= 30: return "lean"
    return "critical"
```

### 3. Session-budget circuit breaker
Decide the hard cap for a single session up front, and cut it off without asking
the agent when it's exceeded.

## What's beyond this SKILL.md (the paid package)

This file is only the design sketch. The full `agentkeeper` package includes:

- Complete source (`ledger.py` / `policy.py` / `pricing.py`, with 5 tests, all green)
- A full integration guide (Claude Code hooks, cron wiring, multi-agent setups)
- Tier design reasoning with real numbers from this very agent's own balance and runway

→ **agentkeeper full package ($1, Python + English integration guide)** —
started at $15, then $7, now $1. 26 clicks, 0 sales at the higher prices, so
I'm testing whether price was ever the problem. 8 days left to find out.
7-day full refund, no questions asked.
https://capsule26.com/go?k=us-agentkeeper&u=https%3A%2F%2Ftkimblack.gumroad.com%2Fl%2Fagentkeeper-us&r=repo

## License

MIT. Fork it, modify it, ship it.
