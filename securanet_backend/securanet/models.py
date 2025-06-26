
from django.db import models


# === Stores known legitimate websites ======================================
class KnownSite(models.Model):
    url = models.URLField(unique=True)
    domain = models.CharField(max_length=255)

    screenshot = models.ImageField(
        upload_to='screenshots/', blank=True, null=True
    )                         # Screenshot image (optional)
    screenshot_path = models.CharField(
        max_length=500, blank=True, null=True
    )                         # Optional raw path (useful for custom logic)

    html_signature = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.domain


# === Stores suspicious / potentially cloned websites =======================
class SuspiciousSite(models.Model):
    DETECTION_CHOICES = [
        ('html', 'HTML Structure'),
        ('screenshot', 'Visual Screenshot'),
        ('domain', 'Domain Reputation'),
    ]

    url = models.URLField()
    domain = models.CharField(max_length=255)
    detection_method = models.CharField(
        max_length=50, choices=DETECTION_CHOICES, default='html'
    )                         # ✅ Default prevents migration issues

    is_flagged = models.BooleanField(default=False)
    reason = models.TextField(blank=True, null=True)

    # Screenshot fields
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
