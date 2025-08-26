from django.core.management.base import BaseCommand
from file_management.models import FileChangeLog, FileAnalysis
from django.db.models import Count, Max, Min
from django.utils import timezone

class Command(BaseCommand):
    help = 'Show log status and database info'

    def handle(self, *args, **options):
        # Get log counts
        log_count = FileChangeLog.objects.count()
        analysis_count = FileAnalysis.objects.count()
        
        self.stdout.write("=" * 50)
        self.stdout.write("SecureNet Log Status")
        self.stdout.write("=" * 50)
        
        # Basic counts
        self.stdout.write(f"Total logs: {log_count}")
        self.stdout.write(f"Total analysis records: {analysis_count}")
        
        # Date ranges
        if log_count > 0:
            newest = FileChangeLog.objects.aggregate(Max('timestamp'))['timestamp__max']
            oldest = FileChangeLog.objects.aggregate(Min('timestamp'))['timestamp__min']
            self.stdout.write(f"\nLog date range:")
            self.stdout.write(f"  Oldest: {oldest}")
            self.stdout.write(f"  Newest: {newest}")
            self.stdout.write(f"  Span: {(newest - oldest).days} days, {(newest - oldest).seconds // 3600} hours")
        
        # Risk level distribution
        self.stdout.write("\nRisk level distribution:")
        risk_counts = FileChangeLog.objects.values('risk_level').annotate(count=Count('id')).order_by('-count')
        for risk in risk_counts:
            level = risk['risk_level'] or 'unknown'
            self.stdout.write(f"  {level}: {risk['count']}")
        
        # Get database size
        from django.db import connection
        import os
        
        cursor = connection.cursor()
        cursor.execute("PRAGMA page_count;")
        page_count = cursor.fetchone()[0]
        cursor.execute("PRAGMA page_size;")
        page_size = cursor.fetchone()[0]
        db_size = page_count * page_size / (1024 * 1024)
        
        self.stdout.write(f"\nDatabase size: {db_size:.2f} MB")
        
        # Retention config
        import json
        from django.conf import settings
        
        self.stdout.write("\nLog retention config:")
        config_file = os.path.join(settings.BASE_DIR, 'monitor_config.json')
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    config = json.load(f)
                retention = config.get('log_retention', {})
                self.stdout.write(f"  Max records: {retention.get('max_records', 'Not set')}")
                self.stdout.write(f"  Days to keep: {retention.get('days_to_keep', 'Not set')}")
                self.stdout.write(f"  Auto cleanup: {'Enabled' if retention.get('auto_cleanup_enabled', False) else 'Disabled'}")
                self.stdout.write(f"  Cleanup interval: {retention.get('cleanup_interval_hours', 'Not set')} hours")
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"  Error reading config: {e}"))
        else:
            self.stdout.write(self.style.WARNING("  Config file not found"))



