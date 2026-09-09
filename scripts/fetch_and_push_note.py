"""
GitHub Actions上で実行する、note.comのRSSを取得・パースしてWebhookにPOSTするスクリプト。
Djangoに依存せず、feedparser + requestsのみで完結する。
core/management/commands/sync_note.py とパースロジックは同一。
"""
import html
import os
import re
import sys
from datetime import datetime, timezone as dt_timezone

import feedparser
import requests

PREFIX_TO_CATEGORY = {
    '経験談': 'experience',
    '個人開発': 'personal',
    'チーム開発': 'team',
}

PREFIX_PATTERN = re.compile(r'^[\[【]\s*(.+?)\s*[\]】]\s*')
TAG_PATTERN = re.compile(r'<[^>]+>')
CONTINUE_LINK_PATTERN = re.compile(r'続きをみる\s*$')


def resolve_category_and_title(raw_title):
    match = PREFIX_PATTERN.match(raw_title)
    if not match:
        return None, raw_title
    prefix = match.group(1)
    category = PREFIX_TO_CATEGORY.get(prefix)
    if category is None:
        return None, raw_title
    clean_title = raw_title[match.end():].strip()
    return category, clean_title


def clean_summary(raw_summary):
    text = TAG_PATTERN.sub('', raw_summary)
    text = html.unescape(text)
    text = CONTINUE_LINK_PATTERN.sub('', text)
    return text.strip()


def resolve_thumbnail(entry):
    thumbnails = getattr(entry, 'media_thumbnail', None)
    if thumbnails:
        return thumbnails[0].get('url', '')
    return ''


def resolve_published_at(entry):
    if getattr(entry, 'published_parsed', None):
        return datetime(*entry.published_parsed[:6], tzinfo=dt_timezone.utc)
    return datetime.now(tz=dt_timezone.utc)


def main():
    rss_url = os.environ['NOTE_RSS_URL']
    endpoint_url = os.environ['SYNC_ENDPOINT_URL']
    token = os.environ['SYNC_SECRET_TOKEN']

    feed = feedparser.parse(rss_url)
    if feed.bozo:
        print(f'WARNING: RSSのパースで警告: {feed.bozo_exception}', file=sys.stderr)

    articles = []
    skipped_count = 0
    for entry in feed.entries:
        category, clean_title = resolve_category_and_title(entry.title)
        if category is None:
            skipped_count += 1
            continue

        articles.append({
            'title': clean_title,
            'url': entry.link,
            'summary': clean_summary(getattr(entry, 'summary', '')),
            'thumbnail_url': resolve_thumbnail(entry),
            'category': category,
            'published_at': resolve_published_at(entry).isoformat(),
        })

    print(f'{len(articles)}件を取得（接頭辞なしのため{skipped_count}件をスキップ）')

    response = requests.post(
        endpoint_url,
        json={'articles': articles},
        headers={'X-Sync-Token': token},
        timeout=30,
    )
    print(f'Webhook response: {response.status_code} {response.text}')

    if response.status_code != 200:
        sys.exit(1)


if __name__ == '__main__':
    main()
