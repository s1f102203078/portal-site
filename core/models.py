from django.db import models


class LearningLog(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    tech_stack = models.CharField(max_length=200, blank=True, help_text="カンマ区切り 例: Django, Python")
    repo_url = models.URLField(blank=True)
    created_at = models.DateField()

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def tech_list(self):
        return [t.strip() for t in self.tech_stack.split(',') if t.strip()]