from django.contrib import admin
from .models import HeaderAnalysisResult

@admin.register(HeaderAnalysisResult)
class HeaderAnalysisResultAdmin(admin.ModelAdmin):
    list_display = ('user', 'submitted_at', 'client_ip')
    search_fields = ('raw_header',)
