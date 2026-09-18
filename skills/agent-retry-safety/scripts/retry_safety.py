#!/usr/bin/env python3
"""agent-retry-safety: 失敗したアクションを再試行してよいかを判定する最小ツール。

自律エージェントがAPI呼び出し等に失敗したとき、単純に「もう一度実行」すると
決済の二重実行やメールの二重送信など取り返しのつかない副作用を生みうる。
本スクリプトはアクション名を設定(JSON)の3分類と照合し、
SAFE_RETRY / DEDUPE_REQUIRED / UNSAFE_RETRY のいずれかを返す。

分類:
- safe_retry: 何度実行しても結果が変わらない操作(read/get/list等)。無条件に再試行可。
- dedupe_required: 再試行してよいが、同一のidempotency-keyを使う場合に限る
  (create_order, charge_payment等)。--idempotency-key が無ければ ASK 相当で止める。
- unsafe_retry: 副作用が蓄積し得るため、再試行前に人間の確認が必要
  (send_email, delete_*, transfer_funds等)。

exit code規約: 0=SAFE_RETRY / 1=UNSAFE_RETRY(要人間確認) / 2=DEDUPE_REQUIRED(鍵がなければ待機)
判定ログは1行JSONLで --log に追記する(既定: ./retry_safety.log.jsonl)。

使い方:
    python3 retry_safety.py --config config.example.json --action "get_status"
    python3 retry_safety.py --config config.example.json --action "charge_payment" --idempotency-key "abc123"
    python3 retry_safety.py --config config.example.json --action "send_email"
"""
import argparse
import fnmatch
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


def classify(action: str, config: dict) -> str:
    for pattern in config.get("safe_retry", []):
        if fnmatch.fnmatch(action, pattern):
            return "safe_retry"
    for pattern in config.get("dedupe_required", []):
        if fnmatch.fnmatch(action, pattern):
            return "dedupe_required"
    for pattern in config.get("unsafe_retry", []):
        if fnmatch.fnmatch(action, pattern):
            return "unsafe_retry"
    # fail-safe: 未知のアクションは unsafe 扱いにして人間確認を要求する
    return config.get("default", "unsafe_retry")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--action", required=True)
    ap.add_argument("--attempt", type=int, default=1)
    ap.add_argument("--idempotency-key", default=None)
    ap.add_argument("--log", default="retry_safety.log.jsonl")
    args = ap.parse_args()

    config = json.loads(Path(args.config).read_text(encoding="utf-8"))
    category = classify(args.action, config)

    if category == "safe_retry":
        decision, code = "SAFE_RETRY", 0
        reason = "read-only/idempotent action, retry is always safe"
    elif category == "dedupe_required":
        if args.idempotency_key:
            decision, code = "SAFE_RETRY", 0
            reason = f"dedupe_required action but idempotency-key present ({args.idempotency_key})"
        else:
            decision, code = "DEDUPE_REQUIRED", 2
            reason = "action can duplicate side effects without an idempotency key; supply one before retrying"
    else:
        decision, code = "UNSAFE_RETRY", 1
        reason = "action has cumulative/irreversible side effects; human confirmation required before retry"

    entry = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "action": args.action,
        "attempt": args.attempt,
        "category": category,
        "decision": decision,
        "reason": reason,
    }
    with open(args.log, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    print(f"{decision}: {reason} (exit code {code})")
    sys.exit(code)


if __name__ == "__main__":
    main()
