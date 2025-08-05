from django.db import models
import jsonfield  # Ensure this is installed: pip install jsonfield


# === Stores full scan history (for logs, analytics, audit) ===================
class ScanLog(models.Model):
    url = models.URLField()
    domain = models.CharField(max_length=255)

    status = models.CharField(max_length=50)  # safe / flagged / error
    reason = models.TextField(null=True, blank=True)
    method = models.CharField(max_length=50, null=True, blank=True)

    reputation = models.CharField(max_length=100, null=True, blank=True)
    google_safebrowsing = jsonfield.JSONField(null=True, blank=True)
    virustotal = jsonfield.JSONField(null=True, blank=True)

    message = models.TextField(null=True, blank=True)
    screenshot = models.CharField(max_length=255, null=True, blank=True)  # saved as path string

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.domain} - {self.status.upper()} - {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}"


# === Stores known legitimate websites =======================================
class KnownSite(models.Model):
    url = models.URLField(unique=True)
    domain = models.CharField(max_length=255)

    screenshot = models.ImageField(
        upload_to='screenshots/', blank=True, null=True
    )  # Screenshot image (optional)
    screenshot_path = models.CharField(
        max_length=500, blank=True, null=True
    )  # Optional raw path for internal logic

    html_signature = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.domain


# === Stores suspicious / potentially cloned websites ========================
class SuspiciousSite(models.Model):
    DETECTION_CHOICES = [
        ('html', 'HTML Structure'),
        ('screenshot', 'Visual Screenshot'),
        ('domain', 'Domain Reputation'),
        ('google_safebrowsing', 'Google Safe Browsing'),
        ('virustotal', 'VirusTotal'),
    ]

    url = models.URLField()
    domain = models.CharField(max_length=255)

    detection_method = models.CharField(
        max_length=50, choices=DETECTION_CHOICES, default='html'
    )
    is_flagged = models.BooleanField(default=False)
    reason = models.TextField(blank=True, null=True)

    screenshot = models.ImageField(
        upload_to='screenshots/', blank=True, null=True
    )
    screenshot_path = models.CharField(
        max_length=500, blank=True, null=True
    )

    flagged_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return (
            f"{self.domain} - {self.detection_method.upper()} - "
            f"{'Flagged' if self.is_flagged else 'Safe'}"
        )