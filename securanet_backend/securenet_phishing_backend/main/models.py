from django.db import models

class PhishingLog(models.Model):
    email = models.CharField(max_length=100)
    password = models.CharField(max_length=255)
    clicked = models.BooleanField(default=False)
    submitted_credentials = models.BooleanField(default=False)
    ip_address = models.CharField(max_length=45, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'main_phishing_simulation'   # Use existing table
        managed = False                   # Prevent Django from altering it
