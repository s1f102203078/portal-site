from datetime import datetime, timezone as dt_timezone

import feedparser
from decouple import config
from django.core.management.base import BaseCommand

from core.models import NoteArticle

# noteの記事に付けたハッシュタグ → カテゴリの対応表
TAG_TO_CATEGORY = {
    '経験談': NoteArticle.CATEGORY_EXPERIENCE,
    '個人開発': NoteArticle.CATEGORY_PERSONAL,
    'チーム開発': NoteArticle.CATEGORY_TEAM,
}


class Command(BaseCommand):
    help = 'noteのRSSフィードを取得し、ハッシュタグからカテゴリを判定してNoteArticleに同期します'

    def handle(self, *args, **options):
        rss_url = config('NOTE_RSS_URL')  # 例: https://note.com/s1f102203078/rss

        feed = feedparser.parse(rss_url)

        if feed.bozo:
            # bozo=True はフィードのパースで何らかの問題があったことを示す
            self.stderr.write(self.style.WARNING(
                f'RSSのパースで警告が発生しました: {feed.bozo_exception}'
            ))

        synced_count = 0

        for entry in feed.entries:
            category = self._resolve_category(entry)
            published_at = self._resolve_published_at(entry)

            NoteArticle.objects.update_or_create(
                url=entry.link,
                defaults={
                    'title': entry.title,
                    'summary': getattr(entry, 'summary', ''),
                    'category': category,
                    'published_at': published_at,
                },
            )
            synced_count += 1

        self.stdout.write(self.style.SUCCESS(f'{synced_count}件のnote記事を同期しました'))

    def _resolve_category(self, entry):
        tags = [t.get('term', '') for t in getattr(entry, 'tags', [])]
        for tag_name, category in TAG_TO_CATEGORY.items():
            if tag_name in tags:
                return category
        # どのハッシュタグにも一致しない場合は「個人開発」を既定値にする
        return NoteArticle.CATEGORY_PERSONAL

    def _resolve_published_at(self, entry):
        if getattr(entry, 'published_parsed', None):
            return datetime(*entry.published_parsed[:6], tzinfo=dt_timezone.utc)
        return datetime.now(tz=dt_timezone.utc)
