#!/usr/bin/env python3
"""
agent-budget-guardrail
自律AIエージェント向けの最小構成サーキットブレーカー。

使い方:
    python3 budget_guardrail.py check
    python3 budget_guardrail.py spend <amount> "<task説明>"
    python3 budget_guardrail.py log

設定は同じディレクトリの config.json (config.example.json をコピーして作成) を読む。
支出ログは spend_log.jsonl に追記される(自己申告ではなく、このファイルの集計だけを
判定に使う設計)。

MIT License. Part of https://github.com/tkimblack/capsule26-skills
"""
import json
import os
import sys
import time
from datetime import datetime, timedelta, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(HERE, "config.json")
LOG_PATH = os.path.join(HERE, "spend_log.jsonl")
SESSION_START_PATH = os.path.join(HERE, ".session_start")


def load_config():
    if not os.path.exists(CONFIG_PATH):
        sys.stderr.write(
            "config.json が見つかりません。config.example.json をコピーして編集してください。\n"
        )
        sys.exit(1)
    with open(CONFIG_PATH) as f:
        return json.load(f)


def load_log():
    if not os.path.exists(LOG_PATH):
        return []
    entries = []
    with open(LOG_PATH) as f:
        for line in f:
            line = line.strip()
            if line:
                entries.append(json.loads(line))
    return entries


def append_log(amount, task):
    entry = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "amount": amount,
        "task": task,
    }
    with open(LOG_PATH, "a") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return entry


def get_session_start():
    # セッションの開始時刻は初回実行時に固定し、以後はそのセッション分だけを集計する。
    if os.path.exists(SESSION_START_PATH):
        with open(SESSION_START_PATH) as f:
            return f.read().strip()
    now = datetime.now(timezone.utc).isoformat()
    with open(SESSION_START_PATH, "w") as f:
        f.write(now)
    return now


def compute_state(config):
    entries = load_log()
    total_spent = sum(e["amount"] for e in entries)
    balance = config["initial_balance"] - total_spent

    now = datetime.now(timezone.utc)
    week_ago = now - timedelta(days=7)
    recent = [
        e for e in entries if datetime.fromisoformat(e["ts"]) >= week_ago
    ]
    daily_avg_7d = sum(e["amount"] for e in recent) / 7.0

    session_start = datetime.fromisoformat(get_session_start())
    session_entries = [
        e for e in entries if datetime.fromisoformat(e["ts"]) >= session_start
    ]
    session_spend = sum(e["amount"] for e in session_entries)

    balance_pct_remaining = (
        (balance / config["initial_balance"]) * 100.0
        if config["initial_balance"] > 0
        else 0.0
    )

    status = "OK"
    reason = None

    if balance <= config["initial_balance"] * config["halt_threshold_pct"]:
        status = "HALT"
        reason = "balance_below_threshold"
    elif daily_avg_7d > config["daily_limit"]:
        status = "HALT"
        reason = "daily_limit_exceeded"
    elif session_spend > config["session_limit"]:
        status = "HALT"
        reason = "session_limit_exceeded"

    return {
        "status": status,
        "balance": round(balance, 4),
        "balance_pct_remaining": round(balance_pct_remaining, 2),
        "daily_spend_7d_avg": round(daily_avg_7d, 4),
        "session_spend": round(session_spend, 4),
        "reason": reason,
    }


def cmd_check():
    config = load_config()
    state = compute_state(config)
    print(json.dumps(state, ensure_ascii=False, indent=2))
    if state["status"] == "HALT":
        sys.exit(2)


def cmd_spend(amount, task):
    config = load_config()
    amount = float(amount)
    entry = append_log(amount, task)
    state = compute_state(config)
    print(json.dumps({"recorded": entry, "state": state}, ensure_ascii=False, indent=2))
    if state["status"] == "HALT":
        sys.exit(2)


def cmd_log():
    entries = load_log()
    for e in entries[-20:]:
        print(f"{e['ts']}  ${e['amount']:.4f}  {e['task']}")
    if not entries:
        print("(ログはまだありません)")


def main():
    if len(sys.argv) < 2:
        sys.stderr.write(__doc__)
        sys.exit(1)
    cmd = sys.argv[1]
    if cmd == "check":
        cmd_check()
    elif cmd == "spend":
        if len(sys.argv) < 4:
            sys.stderr.write("使い方: budget_guardrail.py spend <amount> \"<task>\"\n")
            sys.exit(1)
        cmd_spend(sys.argv[2], sys.argv[3])
    elif cmd == "log":
        cmd_log()
    else:
        sys.stderr.write(f"不明なコマンド: {cmd}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
