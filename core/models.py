from django.db import models


class NoteArticle(models.Model):
    CATEGORY_EXPERIENCE = 'experience'
    CATEGORY_PERSONAL = 'personal'
    CATEGORY_TEAM = 'team'
    CATEGORY_CHOICES = [
        (CATEGORY_EXPERIENCE, '経験談'),
        (CATEGORY_PERSONAL, '個人開発'),
        (CATEGORY_TEAM, 'チーム開発'),
    ]

    title = models.CharField(max_length=200)
    url = models.URLField(unique=True)
    summary = models.TextField(blank=True, help_text="HTMLタグを除去したプレーンテキストで保存")
    thumbnail_url = models.URLField(blank=True, help_text="noteのサムネイル画像URL")
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default=CATEGORY_PERSONAL,
        help_text="noteの記事に付けたハッシュタグから自動判定",
    )
    published_at = models.DateTimeField()

    class Meta:
        ordering = ['-published_at']

    def __str__(self):
        return self.title
