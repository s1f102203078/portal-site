import html
import re
from datetime import datetime, timezone as dt_timezone

import feedparser
from decouple import config
from django.core.management.base import BaseCommand

from core.models import NoteArticle

# タイトル先頭の接頭辞 → カテゴリの対応表
# 例: "[経験談] Gensparkと作る！リアルなWebアプリ開発体験記"
PREFIX_TO_CATEGORY = {
    '経験談': NoteArticle.CATEGORY_EXPERIENCE,
    '個人開発': NoteArticle.CATEGORY_PERSONAL,
    'チーム開発': NoteArticle.CATEGORY_TEAM,
}

# 例: "[経験談] " や "【経験談】" のどちらでも拾えるように、括弧の種類を許容する
PREFIX_PATTERN = re.compile(r'^[\[【]\s*(.+?)\s*[\]】]\s*')

# HTMLタグを除去するための簡易パターン（noteのdescriptionはシンプルなタグのみのため正規表現で十分）
TAG_PATTERN = re.compile(r'<[^>]+>')
# "続きをみる" のリンク文言はdescription末尾に必ず付いてくるので除去する
CONTINUE_LINK_PATTERN = re.compile(r'続きをみる\s*$')


class Command(BaseCommand):
    help = (
        'noteのRSSフィードを取得し、タイトル先頭の接頭辞（例: [経験談]）から'
        'カテゴリを判定してNoteArticleに同期します'
    )

    def handle(self, *args, **options):
        rss_url = config('NOTE_RSS_URL')

        feed = feedparser.parse(rss_url)

        if feed.bozo:
            self.stderr.write(self.style.WARNING(
                f'RSSのパースで警告が発生しました: {feed.bozo_exception}'
            ))

        synced_count = 0
        skipped_count = 0

        for entry in feed.entries:
            category, clean_title = self._resolve_category_and_title(entry.title)

            if category is None:
                skipped_count += 1
                continue

            published_at = self._resolve_published_at(entry)
            summary = self._clean_summary(getattr(entry, 'summary', ''))
            thumbnail_url = self._resolve_thumbnail(entry)

            NoteArticle.objects.update_or_create(
                url=entry.link,
                defaults={
                    'title': clean_title,
                    'summary': summary,
                    'thumbnail_url': thumbnail_url,
                    'category': category,
                    'published_at': published_at,
                },
            )
            synced_count += 1

        self.stdout.write(self.style.SUCCESS(
            f'{synced_count}件のnote記事を同期しました（接頭辞なしのため{skipped_count}件をスキップ）'
        ))

    def _resolve_category_and_title(self, raw_title):
        match = PREFIX_PATTERN.match(raw_title)
        if not match:
            return None, raw_title

        prefix = match.group(1)
        category = PREFIX_TO_CATEGORY.get(prefix)
        if category is None:
            return None, raw_title

        clean_title = raw_title[match.end():].strip()
        return category, clean_title

    def _clean_summary(self, raw_summary):
        """HTMLタグを除去し、'続きをみる'のリンク文言も取り除いてプレーンテキスト化する"""
        text = TAG_PATTERN.sub('', raw_summary)
        text = html.unescape(text)
        text = CONTINUE_LINK_PATTERN.sub('', text)
        return text.strip()

    def _resolve_thumbnail(self, entry):
        """feedparserがMedia RSS(<media:thumbnail>)をentry.media_thumbnailとして解釈してくれる"""
        thumbnails = getattr(entry, 'media_thumbnail', None)
        if thumbnails:
            return thumbnails[0].get('url', '')
        return ''

    def _resolve_published_at(self, entry):
        if getattr(entry, 'published_parsed', None):
            return datetime(*entry.published_parsed[:6], tzinfo=dt_timezone.utc)
        return datetime.now(tz=dt_timezone.utc)
