---
name: agent-approval-gate
description: 自律AIエージェントの各アクションを実行前に「許可 / 拒否 / 要確認」に自動分類する軽量ゲート。ルールをJSONで定義し、危険な操作(支払い・削除・外部送信など)を人間の確認待ちに落とし込む。Claude Code のフック(PreToolUse等)や自作ハーネスから呼び出せる。
license: MIT
---

# agent-approval-gate

自律AIエージェント(Claude Code含む)が「何でも自動実行してよいか」を毎回人間が判断するのは
現実的ではありません。一方で全自動は暴走リスクを増やします。
このスキルは **ルールベースの最小限の承認ゲート** を提供します。

## できること

- アクション名・パラメータ文字列をルール(allow / deny / ask のパターンリスト)と照合
- 判定結果を `ALLOW` / `DENY` / `ASK` の3値で返す(exit codeでも判定可能)
- 判定ログを1行JSONLで追記保存(誰が・何を・いつ・どう判定されたか)
- ルールにマッチしないアクションは既定で `ASK`(fail-safe: 不明なものは止める)

## 使い方

```bash
python3 scripts/approval_gate.py --config config.example.json --action "restart_service" --detail "nginx"
# => ASK: no explicit rule matched, defaulting to ASK (fail-safe) (exit code 2)

python3 scripts/approval_gate.py --config config.example.json --action "read_file"
# => ALLOW: matched allow pattern 'read_file' (exit code 0)

python3 scripts/approval_gate.py --config config.example.json --action "send_payment" --detail "$50 to acme"
# => DENY: matched deny pattern 'send_payment' (exit code 1)

python3 scripts/approval_gate.py --config config.example.json --action "delete_file" --detail "rm -rf /tmp/x"
# => DENY: matched deny pattern 'rm -rf /' (detailにマッチしたコマンド文字列を含む場合もdenyされる)
```

exit code規約: `0=ALLOW` / `1=DENY` / `2=ASK`。CI・フック・シェルスクリプトから
`if`で直接分岐できます。

## ルール設定(config.example.json)

```json
{
  "allow": ["read_file", "list_dir", "get_*"],
  "deny": ["send_payment", "delete_prod_*", "rm -rf /"],
  "ask_default": true
}
```

パターンは前方一致・`*`ワイルドカードに対応(依存ライブラリなし、標準ライブラリのみ)。

## この先にあるもの(有償ガイドの範囲)

このスキルは「動く最小分類器」です。実務ではこれだけでは足りません:
- どのカテゴリのアクションを承認待ちにすべきかの**分類表(30項目以上)**
- 承認待ちが積み重なったときの**べき等性・再試行設計**
- 失敗時に自動リトライしてよい操作とダメな操作の切り分け
- Claude Code / Agent Skills 特有のトークンコスト削減チェックリスト

これらを整理したのが「自律AIエージェント運用実践ガイド」(¥980・日本語PDF)です。
→ https://tkimblack.gumroad.com/l/jp-agent-ops-guide

## ライセンス

MIT。改変・組み込み自由です。
