from django.db import models
import json

class FileAnalysis(models.Model):
    file_path = models.CharField(max_length=1024)
    content_hash = models.CharField(max_length=64, blank=True, null=True)
    risk_score = models.FloatField(default=0.0)
    risk_level = models.CharField(max_length=20, default='unknown')
    analysis_result = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.file_path} - {self.risk_level}"
    
    class Meta:
        verbose_name_plural = "File Analyses"
        indexes = [
            models.Index(fields=['file_path']),
            models.Index(fields=['risk_level']),
            models.Index(fields=['created_at']),
            models.Index(fields=['content_hash']),
        ]


class FileChangeLog(models.Model):
    # Your existing fields here...
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)  # Add index
    file_path = models.TextField()
    change_type = models.CharField(max_length=20)
    risk_level = models.CharField(max_length=20, db_index=True)  # Add index
    recommendation = models.TextField(null=True, blank=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['-timestamp']),  # Index for reverse timestamp queries
            models.Index(fields=['risk_level', '-timestamp']),  # Compound index
        ]