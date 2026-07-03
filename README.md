# Portal Site

自分用の個人ポータルサイトです。公開ポートフォリオ(About/学習ログ)と、非公開ダッシュボード(家計・投資など)の二層構成になっています。

## 技術スタック

- Django + SQLite(MVP段階)
- Tailwind CSS(CDN版)
- 今後: Notion API連携、React/TypeScript化を予定

## セットアップ

\`\`\`bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # SECRET_KEYなどを設定
python manage.py migrate
python manage.py runserver
\`\`\`

## 開発フロー

git-flowに従ってブランチを運用しています。

- `main`: 本番リリース用
- `develop`: 開発のベースブランチ
- `feature/*`: 機能単位のブランチ

詳細なコマンドは [docs/git-workflow.md](docs/git-workflow.md) を参照してください。
