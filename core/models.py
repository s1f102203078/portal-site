from django.db import models


class NoteArticle(models.Model):
    CATEGORY_SELF = 'self'
    CATEGORY_DEV = 'dev'
    CATEGORY_EVENT = 'event'
    CATEGORY_TOPIC = 'topic'
    CATEGORY_CHOICES = [
        (CATEGORY_SELF, '自己・業界・企業理解'),
        (CATEGORY_DEV, '開発の記録と学び'),
        (CATEGORY_EVENT, '就活イベント・インターンでの振り返り'),
        (CATEGORY_TOPIC, '時事・興味の考察'),
    ]

    title = models.CharField(max_length=200)
    url = models.URLField(unique=True)
    summary = models.TextField(blank=True, help_text="HTMLタグを除去したプレーンテキストで保存")
    thumbnail_url = models.URLField(blank=True, help_text="noteのサムネイル画像URL")
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default=CATEGORY_DEV,
        help_text="noteの記事タイトル先頭の接頭辞（例: 【開発の記録と学び】）から自動判定",
    )
    published_at = models.DateTimeField()

    class Meta:
        ordering = ['-published_at']

    def __str__(self):
        return self.title
