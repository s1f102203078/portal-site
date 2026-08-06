from django.contrib import admin
from .models import NoteArticle


@admin.register(NoteArticle)
class NoteArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'published_at')
    list_filter = ('category',)
    ordering = ('-published_at',)
