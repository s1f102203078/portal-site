# Git運用フロー

## セットアップ

git-flow拡張が必要です(Ubuntu/WSL)。

\`\`\`bash
sudo apt install git-flow
git flow init -d
\`\`\`

## 日常の開発サイクル

新機能に着手する時:

\`\`\`bash
git flow feature start <feature-name>
\`\`\`

完了したら develop にマージ:

\`\`\`bash
git flow feature finish <feature-name>
git push origin develop
\`\`\`

## 実績ログ

| 日付 | ブランチ | 内容 |
|---|---|---|
| 2026-07-04 | feature/about-page | coreアプリ・Aboutページ実装 |

## トラブルシュート

- `git clone` をリポジトリ内で実行すると空フォルダがネストする → `git remote add` を使う
- `TIME_ZONE` は `Asia/Tokyo`(先頭のみ大文字、IANA準拠)
