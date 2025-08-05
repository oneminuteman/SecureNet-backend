from django.db import models

class FileAnalysis(models.Model):
    file_path = models.TextField()
    content_hash = models.CharField(max_length=64)
    risk_score = models.FloatField()
    risk_level = models.CharField(max_length=20)
    analysis_result = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['file_path']),
            models.Index(fields=['risk_level']),
            models.Index(fields=['created_at']),
        ]

class FileChangeLog(models.Model):
    CHANGE_TYPES = [
        ('created', 'Created'),
        ('modified', 'Modified'),
        ('deleted', 'Deleted'),
        ('renamed', 'Renamed'),
    ]
    
    RISK_LEVELS = [
        ('safe', 'Safe'),
        ('suspicious', 'Suspicious'),
        ('dangerous', 'Dangerous'),
    ]

    file_path = models.TextField()
    change_type = models.CharField(max_length=20, choices=CHANGE_TYPES)
    timestamp = models.DateTimeField(auto_now_add=True)
    analysis = models.ForeignKey(FileAnalysis, on_delete=models.CASCADE, null=True, blank=True)
    metadata = models.JSONField(default=dict)
    dedup_key = models.CharField(max_length=32, unique=True, null=True)
    recommendation = models.TextField(null=True, blank=True)  # Added this field
    risk_level = models.CharField(max_length=20, choices=RISK_LEVELS, default='safe')  # Added this field

    class Meta:
        indexes = [
            models.Index(fields=['file_path', 'timestamp']),
            models.Index(fields=['change_type']),
            models.Index(fields=['risk_level']),
        ]

    def __str__(self):
        return f"{self.change_type} - {self.file_path} ({self.timestamp})"