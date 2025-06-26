
from django.contrib import admin
from .models import KnownSite, SuspiciousSite


# === Admin View for SuspiciousSite ===
@admin.register(SuspiciousSite)
class SuspiciousSiteAdmin(admin.ModelAdmin):
    list_display = ('domain', 'url', 'detection_method', 'is_flagged', 'flagged_at')
    list_filter = ('detection_method', 'is_flagged')
    search_fields = ('domain', 'url', 'reason')


# === Simple Registration for KnownSite ===
@admin.register(KnownSite)
class KnownSiteAdmin(admin.ModelAdmin):
    list_display = ('domain', 'url', 'created_at')
    search_fields = ('domain', 'url')
