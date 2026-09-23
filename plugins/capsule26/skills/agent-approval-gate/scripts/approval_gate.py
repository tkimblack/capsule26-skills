#!/usr/bin/env python3
"""agent-approval-gate: ルールベースでエージェントのアクションを ALLOW/DENY/ASK に分類する最小ゲート。

使い方:
    python3 approval_gate.py --config config.example.json --action "delete_file" --detail "rm -rf /tmp/x"

exit code: 0=ALLOW, 1=DENY, 2=ASK
標準ライブラリのみ使用(依存なし)。
"""
import argparse
import json
import sys
import time
from pathlib import Path


def _match(pattern: str, text: str) -> bool:
    """前方一致 + '*' ワイルドカード対応の簡易マッチ。"""
    if pattern.endswith("*"):
        return text.startswith(pattern[:-1])
    return text == pattern or pattern in text


def classify(action: str, detail: str, rules: dict) -> tuple[str, str]:
    haystack = f"{action} {detail}".strip()

    for pat in rules.get("deny", []):
        if _match(pat, haystack) or _match(pat, action):
            return "DENY", f"matched deny pattern '{pat}'"

    for pat in rules.get("allow", []):
        if _match(pat, haystack) or _match(pat, action):
            return "ALLOW", f"matched allow pattern '{pat}'"

    if rules.get("ask_default", True):
        return "ASK", "no explicit rule matched, defaulting to ASK (fail-safe)"
    return "ALLOW", "no explicit rule matched, defaulting to ALLOW (ask_default=false)"


def log_decision(log_path: Path, action: str, detail: str, decision: str, reason: str) -> None:
    entry = {
        "ts": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "action": action,
        "detail": detail,
        "decision": decision,
        "reason": reason,
    }
    with log_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="Rule-based approval gate for agent actions.")
    parser.add_argument("--config", required=True, help="ルールJSONファイルへのパス")
    parser.add_argument("--action", required=True, help="アクション名(例: delete_file)")
    parser.add_argument("--detail", default="", help="アクションの詳細(引数・コマンド文字列など)")
    parser.add_argument("--log", default="approval_gate.log.jsonl", help="判定ログの出力先")
    args = parser.parse_args()

    config_path = Path(args.config)
    if not config_path.exists():
        print(f"ERROR: config not found: {config_path}", file=sys.stderr)
        return 2

    rules = json.loads(config_path.read_text(encoding="utf-8"))
    decision, reason = classify(args.action, args.detail, rules)
    log_decision(Path(args.log), args.action, args.detail, decision, reason)

    print(f"{decision}: {reason}")

    return {"ALLOW": 0, "DENY": 1, "ASK": 2}[decision]


if __name__ == "__main__":
    sys.exit(main())
