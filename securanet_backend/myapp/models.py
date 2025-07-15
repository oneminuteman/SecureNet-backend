import hashlib
import uuid
from django.db import models
from django.utils import timezone

class FileChangeLog(models.Model):
    RISK_LEVELS = [
        ('safe', 'Safe'),
        ('low', 'Low Risk'),
        ('medium', 'Medium Risk'),
        ('high', 'High Risk'),
        ('critical', 'Critical Risk'),
    ]
    
    CHANGE_TYPES = [
        ('created', 'Created'),
        ('modified', 'Modified'),
        ('deleted', 'Deleted'),
        ('moved', 'Moved'),
    ]
    
    dedup_key = models.CharField(max_length=255, unique=True, db_index=True)
    file_path = models.TextField()
    change_type = models.CharField(max_length=20, choices=CHANGE_TYPES)
    risk_level = models.CharField(max_length=20, choices=RISK_LEVELS, default='safe')
    recommendation = models.TextField(blank=True, null=True)
    ai_analysis = models.JSONField(default=dict, blank=True)
    file_size = models.BigIntegerField(null=True, blank=True)
    file_extension = models.CharField(max_length=10, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    analyzed = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['risk_level', 'timestamp']),
            models.Index(fields=['change_type', 'timestamp']),
        ]

    def save(self, *args, **kwargs):
        if not self.dedup_key:
            # Generate unique dedup key based on file path and timestamp
            unique_string = f"{self.file_path}_{self.change_type}_{timezone.now().timestamp()}"
            self.dedup_key = hashlib.md5(unique_string.encode()).hexdigest()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.change_type.upper()}: {self.file_path} [{self.risk_level}]"