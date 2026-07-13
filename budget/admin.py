from django.contrib import admin
from .models import Transaction, SyncLog


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('date', 'category', 'amount', 'synced_at')
    list_filter = ('category',)
    ordering = ('-date',)


@admin.register(SyncLog)
class SyncLogAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'status', 'synced_count')
    readonly_fields = ('created_at',)