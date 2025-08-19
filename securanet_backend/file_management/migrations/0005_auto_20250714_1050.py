from django.db import migrations
import hashlib
from django.utils import timezone

def populate_dedup_keys(apps, schema_editor):
    FileChangeLog = apps.get_model("file_management", "FileChangeLog")  # historical model
    if not hasattr(FileChangeLog, "dedup_key"):
        # Field doesn't exist yet at this migration point, skip
        return

    for log in FileChangeLog.objects.filter(dedup_key__isnull=True):
        log.dedup_key = f"{log.file_path}_{log.change_type}_{log.timestamp}"
        log.save(update_fields=["dedup_key"])


def reverse_populate_dedup_keys(apps, schema_editor):
    # This is irreversible, so we'll just pass
    pass

class Migration(migrations.Migration):
    dependencies = [
        ('file_management', '0001_initial'),  # Replace with your actual previous migration
    ]

    operations = [
        migrations.RunPython(populate_dedup_keys, reverse_populate_dedup_keys),
    ]