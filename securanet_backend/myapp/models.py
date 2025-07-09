from django.db import models
from django.utils import timezone

# Create youfrom django.db import models



class FileChangeLog(models.Model):
    file_path = models.TextField()
    change_type = models.CharField(max_length=20)
    risk_level = models.CharField(max_length=20, default='safe')
    recommendation = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    dedup_key = models.CharField(max_length=255, unique=True, blank=True, null=True)  # 🔥 New


    def __str__(self):
        return f"{self.change_type.upper()}: {self.file_path}"

