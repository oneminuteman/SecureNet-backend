from django.db import models
from django.contrib.auth import get_user_model

# Create your models here.

class HeaderAnalysisResult(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    submitted_at = models.DateTimeField(auto_now_add=True)
    raw_header = models.TextField()
    result_json = models.JSONField()
    client_ip = models.GenericIPAddressField(null=True, blank=True)

    def __str__(self):
        return f"Analysis by {self.user} at {self.submitted_at}"

class HeaderSubmission(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, null=True, blank=True)
    raw_header = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"HeaderSubmission by {self.user} at {self.submitted_at}"

class EmailThreatLog(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True, blank=True)
    event_type = models.CharField(max_length=100)
    details = models.JSONField()
    related_header = models.ForeignKey(HeaderSubmission, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"ThreatLog {self.event_type} at {self.timestamp}"
