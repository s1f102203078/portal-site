from django.db import models


class Transaction(models.Model):
    notion_page_id = models.CharField(max_length=100, unique=True)
    date = models.DateField()
    category = models.CharField(max_length=100, blank=True)
    amount = models.IntegerField()
    memo = models.TextField(blank=True)
    synced_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.date} {self.category} {self.amount}円"


class SyncLog(models.Model):
    STATUS_CHOICES = [
        ('success', '成功'),
        ('failed', '失敗'),
    ]

    source = models.CharField(max_length=50, default='notion_budget')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    synced_count = models.IntegerField(default=0)
    error_message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.created_at:%Y-%m-%d %H:%M} - {self.status}"