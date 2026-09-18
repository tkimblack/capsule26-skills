---
name: agent-budget-guardrail
description: 自律AIエージェントの支出を記録し、予算の閾値(残高割合・日次上限・セッション上限)を超えたら自動的にHALTを返す最小構成のサーキットブレーカー。コストが発生する行動の前に必ず呼び出す。
---

# Agent Budget Guardrail

自律的に動くAIエージェントが、予算を使い切って「気づいたら残高ゼロ」になることを防ぐための
最小構成のガードレールです。プロンプトのテクニックではなく、実際に状態を永続化して
判定するコードです。

## いつ使うか

- コストが発生する行動(API呼び出し・外部サービス利用・購入など)を実行する**前**に、
  必ず `check_budget()` を呼んで現在の状態を確認する。
- セッション開始時に、今のセッションでどれだけ使ってよいかを確認する。
- 行動が終わったら `record_spend()` で実際にかかった金額を記録する。

## セットアップ

```bash
cd scripts
cp config.example.json config.json
# config.json の initial_balance / daily_limit / session_limit / halt_threshold_pct を編集
```

## 使い方

```bash
# 現在の予算状態を確認(コストが発生する行動の前に必ず実行)
python3 budget_guardrail.py check

# 支出を記録(行動が終わった後に実行)
python3 budget_guardrail.py spend 0.42 "gpt-4oでの要約タスク"

# 直近の支出ログを見る
python3 budget_guardrail.py log
```

`check` の出力の `status` が `HALT` の場合、エージェントはそれ以上コストが発生する
行動を取らず、人間の確認を待つように設計してください。

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

`HALT` の判定基準(いずれか一つでも該当すれば HALT):

1. 残高が `initial_balance * halt_threshold_pct` を下回った
2. 直近7日の日次支出移動平均が `daily_limit` を超えた
3. 今セッションの累計支出が `session_limit` を超えた

## 設計思想

- **自己申告ではなく、記録された事実だけで判定する。** ログファイル(`spend_log.jsonl`)は
  追記専用にし、判定ロジックはそのログの集計値だけを見る。
- **停止はデフォルト側に倒す。** 判定条件のいずれかに該当すれば理由を問わず `HALT`。
  再開は人間の確認(config.jsonのリセット)を必要とする。
- これは「コスト管理」の最小実装です。失敗対応(べき等性・段階的権限)、
  承認が必要な操作の分類、Claude Code / Agent Skills向けのトークン削減チェックリストなど、
  運用の全体設計は [自律AIエージェント運用実践ガイド](https://tkimblack.gumroad.com/l/jp-agent-ops-guide)
  （¥980・日本語）にまとめています。

## ライセンス

MIT
