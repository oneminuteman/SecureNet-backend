from django.db import migrations
import hashlib
from django.utils import timezone

def populate_dedup_keys(apps, schema_editor):
    FileChangeLog = apps.get_model('myapp', 'FileChangeLog')
    
    for log in FileChangeLog.objects.filter(dedup_key__isnull=True):
        unique_string = f"{log.file_path}_{log.change_type}_{log.timestamp.timestamp()}"
        log.dedup_key = hashlib.md5(unique_string.encode()).hexdigest()
        log.save()

def reverse_populate_dedup_keys(apps, schema_editor):
    # This is irreversible, so we'll just pass
    pass

class Migration(migrations.Migration):
    dependencies = [
        ('myapp', '0001_initial'),  # Replace with your actual previous migration
    ]

    operations = [
        migrations.RunPython(populate_dedup_keys, reverse_populate_dedup_keys),
    ]