from django.contrib import admin
from .models import Target, PriceHistory

# Register your models here.

@admin.register(Target)
class TargetAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'current_price', 'target_price', 'is_active', 'updated_at')
    list_filter = ('is_active', 'updated_at')
    search_fields = ('url', 'title')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(PriceHistory)
class PriceHistoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'target', 'price', 'created_at')
    list_filter = ('created_at',)
    readonly_fields = ('created_at',)