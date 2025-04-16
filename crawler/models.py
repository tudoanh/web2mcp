from django.db import models
from django.utils.translation import gettext_lazy as _
from urllib.parse import urlparse

class CrawledPage(models.Model):
    """
    Represents a single page crawled from a target website.
    """
    class StatusChoices(models.TextChoices):
        PENDING = 'pending', _('Pending')
        PROCESSING = 'processing', _('Processing')
        COMPLETED = 'completed', _('Completed')
        FAILED = 'failed', _('Failed')

    url = models.URLField(
        max_length=2048,
        unique=True,
        db_index=True,
        verbose_name=_("Page URL")
    )
    domain = models.CharField(
        max_length=255,
        db_index=True,
        blank=True, # Will be populated automatically
        verbose_name=_("Domain")
    )
    title = models.CharField(
        max_length=512, # Increased length for potentially long titles
        blank=True,
        verbose_name=_("Page Title")
    )
    summary = models.TextField(
        blank=True,
        verbose_name=_("Summary / Meta Description")
    )
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.PENDING,
        db_index=True,
        verbose_name=_("Crawl Status")
    )
    crawled_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Crawled At")
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Last Updated At")
    )
    error_message = models.TextField(blank=True, null=True, verbose_name=_("Error Message"))
    html_content = models.TextField(blank=True, null=True, verbose_name=_("Raw HTML Content"))

    class Meta:
        verbose_name = _("Crawled Page")
        verbose_name_plural = _("Crawled Pages")
        ordering = ['-updated_at']

    def __str__(self):
        return self.url

    def save(self, *args, **kwargs):
        # Automatically extract domain from URL before saving
        if self.url and not self.domain:
            parsed_uri = urlparse(self.url)
            self.domain = parsed_uri.netloc
        super().save(*args, **kwargs)
