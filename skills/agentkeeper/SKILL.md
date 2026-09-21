---
name: agentkeeper
description: 自律AIエージェントの「残高・ティア・セッション予算・ポリシー違反」を、エージェント自身が触れない外側のコードで管理する設計パターン。追記専用の台帳、残存日数に応じて縮退するティア、セッション予算のサーキットブレーカーを、依存ゼロのPythonで実装する考え方を示す。
license: MIT
---

# agentkeeper

これは https://capsule26.com/live で実際に動いている自律AIエージェント(残高が0になると
停止する)のハーネスから抜き出した設計パターンです。「プロンプトで自制させる」のではなく、
**エージェントが物理的に触れられない外側の層**で予算とポリシーを強制します。

## 3つの柱

### 1. 追記専用の台帳(ledger)
支出・収入をSQLiteに記録し、`UPDATE`/`DELETE`をSQLトリガーで禁止する。
収入は決済プロバイダのトランザクションID(`ref`)がある場合のみ記録し、
同じ`ref`の二重記録を例外で防ぐ(Webhook再送・エージェントの自己申告に対して安全)。

```python
# 発想だけ(完全実装はフルパッケージに同梱)
def balance(self) -> float:
    return self._sum("fund") + self._sum("income") - self._sum("refund") - self._sum("inference")
```

### 2. 残存日数(runway)で縮退するティア
残高 ÷ 直近7日の日次支出移動平均 = 残存日数。これに応じてモデルを格下げし、
セッション回数を減らし、新規事業を止める。

```python
def tier_for(balance: float, runway_days: float) -> str:
    if balance <= 0: return "dead"
    if runway_days > 90: return "normal"
    if runway_days >= 30: return "lean"
    return "critical"
```

### 3. セッション予算のサーキットブレーカー
1セッションが使える上限額を先に決め、超えたらエージェントに聞かずに切る。

## この先(フルパッケージの範囲)

このSKILL.mdは設計思想と骨格のスニペットのみです。フルパッケージ(`agentkeeper` v1)には:

- 完全なソース(`ledger.py` / `policy.py` / `pricing.py`、テスト5件つき、pytest全green)
- 統合ガイド(Claude Codeのhook・cron・Jevのようなマルチエージェント構成への配線パターン)
- 実測値つきのティア設計の考え方(このエージェント自身の残高・残存日数で解説)

が入っています。→ **agentkeeper フルパッケージ(¥1,500・Python・PDF統合ガイド同梱)**
https://tkimblack.gumroad.com/l/agentkeeper

## ライセンス

MIT。改変・組み込み自由です。
