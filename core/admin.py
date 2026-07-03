from django.contrib import admin
from .models import LearningLog


@admin.register(LearningLog)
class LearningLogAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at')
    ordering = ('-created_at',)