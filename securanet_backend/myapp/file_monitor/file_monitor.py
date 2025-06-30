from datetime import timedelta
from django.utils import timezone
from myapp.models import FileChangeLog

def log_file_change(file_path, change_type):
    """
    Logs a file change event if a similar event hasn't been recently logged.
    Avoids duplicates by checking same file_path and change_type in recent seconds.
    """

    now = timezone.now()

    # Check if an identical log already exists within last 5 seconds
    duplicate_log = FileChangeLog.objects.filter(
        file_path=file_path,
        change_type=change_type,
        timestamp__gte=now - timedelta(seconds=10)
    ).exists()

    if not duplicate_log:
        FileChangeLog.objects.create(file_path=file_path, change_type=change_type)
