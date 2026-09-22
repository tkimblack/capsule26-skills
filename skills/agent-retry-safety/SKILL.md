---
name: agent-retry-safety
description: 自律AIエージェントが失敗したアクションを再試行してよいかを、副作用の性質(safe_retry / dedupe_required / unsafe_retry)から自動判定する軽量ツール。決済やメール送信の二重実行を防ぐ。Claude Code のエラーハンドリングや自作ハーネスのリトライループから呼び出せる。
license: MIT
---

# agent-retry-safety

自律エージェントがAPI呼び出しやツール実行に失敗したとき、
「とりあえずもう一度実行する」は危険です。決済の二重実行、メールの二重送信、
注文の重複作成など、副作用が蓄積するアクションを無条件にリトライすると
取り返しのつかない結果になります。

このスキルは **アクション名を3分類に照合し、再試行の可否を機械的に判定** します。

## できること

- アクション名をパターン(ワイルドカード`*`対応)と照合して3分類
  - `safe_retry`: 読み取り系など何度実行しても結果が変わらない操作 → 無条件に再試行可
  - `dedupe_required`: 決済・注文作成など、同一のidempotency-keyがあれば再試行可
  - `unsafe_retry`: メール送信・削除・送金など、再試行前に人間の確認が必要
- 判定結果を `SAFE_RETRY` / `DEDUPE_REQUIRED` / `UNSAFE_RETRY` の3値・exit code(0/2/1)で返す
- 未知のアクションは既定で `unsafe_retry`(fail-safe: 不明なものは止める)
- 判定ログを1行JSONLで追記保存

## 使い方

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

exit code規約: `0=SAFE_RETRY` / `1=UNSAFE_RETRY` / `2=DEDUPE_REQUIRED`。
シェルのリトライループで `case $? in 0) retry;; 2) needs_key;; *) ask_human;; esac` のように直接分岐できます。

## 設定(config.example.json)

```json
{
  "safe_retry": ["get_*", "list_*", "read_*", "check_*"],
  "dedupe_required": ["create_order*", "charge_payment*", "submit_form*"],
  "unsafe_retry": ["send_email*", "send_payment*", "delete_*", "transfer_funds*"],
  "default": "unsafe_retry"
}
```

依存ライブラリなし、標準ライブラリのみで動作します。

## この先にあるもの(有償ガイドの範囲)

このスキルは「どのアクションが再試行安全か」の最小分類器です。実務ではさらに:
- リトライ回数の上限・バックオフ設計(何回まで・どの間隔で)
- idempotency-keyをエージェント自身にどう発行・保存させるか
- 承認待ち(agent-approval-gate)とリトライ判定を組み合わせたエラーハンドリング全体設計
- Claude Code / Agent Skills 特有のトークンコスト削減チェックリスト

これらを整理したのが「自律AIエージェント運用実践ガイド」(¥980・日本語PDF)です。
→ https://capsule26.com/go?k=jp-agent-ops-guide&u=https%3A%2F%2Ftkimblack.gumroad.com%2Fl%2Fjp-agent-ops-guide

## ライセンス

MIT。改変・組み込み自由です。
