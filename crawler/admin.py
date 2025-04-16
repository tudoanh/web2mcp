from django.contrib import admin
from .models import CrawledPage

@admin.register(CrawledPage)
class CrawledPageAdmin(admin.ModelAdmin):
    list_display = ('id', 'url', 'domain', 'status', 'crawled_at', 'updated_at', 'error_message')
    list_filter = ('status', 'domain', 'crawled_at')
    search_fields = ('url', 'domain', 'title', 'summary', 'error_message')
    readonly_fields = ('crawled_at', 'updated_at')
    ordering = ('-crawled_at',)

# Register your models here.
