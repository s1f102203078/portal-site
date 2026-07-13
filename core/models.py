from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class LearningLog(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(help_text="一覧ページに表示する短い要約")
    body = models.TextField(blank=True, help_text="Markdown記法で本文を書けます")
    cover_image = models.ImageField(upload_to='learning_covers/', blank=True, null=True)
    tech_stack = models.CharField(max_length=200, blank=True, help_text="カンマ区切り 例: Django, Python")
    repo_url = models.URLField(blank=True)
    created_at = models.DateField()

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def tech_list(self):
        return [t.strip() for t in self.tech_stack.split(',') if t.strip()]

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title, allow_unicode=True)
            slug = base_slug
            counter = 1
            while LearningLog.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('core:learning_detail', kwargs={'slug': self.slug})