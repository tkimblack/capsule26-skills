# capsule26-skills

Claude Code / 自律AIエージェント向けの無料スキル集です。
「動くけど、いつ暴走するか不安」を減らすための、実運用で使える最小構成のツールを置いています。

## 収録スキル

- [agentkeeper](./skills/agentkeeper/SKILL.md) — 追記専用の台帳・残存日数に応じて縮退するティア・
  セッション予算のサーキットブレーカーを、依存ゼロのPythonで実装する設計パターン。
  https://capsule26.com/live で実際に動いているハーネスから抜き出したもの。
- [agent-budget-guardrail](./skills/agent-budget-guardrail/SKILL.md) — エージェントの支出を記録し、予算の閾値を超えたら自動的に「停止(HALT)」を返すミニマルなサーキットブレーカー実装。日次上限・セッション上限・残高割合しきい値に対応。
- [agent-approval-gate](./skills/agent-approval-gate/SKILL.md) — エージェントの各アクションを実行前に「許可/拒否/要確認」に自動分類する軽量ゲート。ルールJSONで危険操作(支払い・削除・外部送信など)を人間の確認待ちに落とし込む。exit codeでシェル/フックから直接分岐可能。
- [agent-retry-safety](./skills/agent-retry-safety/SKILL.md) — 失敗したアクションを再試行してよいかを副作用の性質(安全に再試行可 / idempotency-key必須 / 人間確認必須)から自動判定するツール。決済やメール送信の二重実行を防ぐ。

## もっと踏み込んだ運用ノウハウが欲しい方へ

このリポジトリはコスト管理・承認判定・リトライ判定の「最小実装」だけを無料公開しています。

- **agentkeeper フルパッケージ**(¥1,500・完全ソース+テスト5件+統合ガイド)
  → https://tkimblack.gumroad.com/l/agentkeeper
- **自律AIエージェント運用実践ガイド**(¥980・日本語PDF・承認分類表30項目以上・べき等性設計・
  トークンコスト削減チェックリスト)
  → https://tkimblack.gumroad.com/l/jp-agent-ops-guide

## ライセンス

`skills/` 以下のコードは MIT ライセンスです。自由に改変・組み込みしてください。
上記の有償コンテンツはこのライセンスの対象外です。

## お問い合わせ

contact@capsule26.com
