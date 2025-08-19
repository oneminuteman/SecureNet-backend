from django.core.management.base import BaseCommand
import os
import json
import time
from django.conf import settings
from file_management.file_monitor.watcher import get_monitor_thread

class Command(BaseCommand):
    help = 'Check the status of the file monitoring system'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("SecureNet Monitor Diagnostic Tool"))
        self.stdout.write("=" * 60)
        
        # Check if monitor_config.json exists and is valid
        config_file = os.path.join(settings.BASE_DIR, 'monitor_config.json')
        self.stdout.write(f"Looking for config file: {config_file}")
        
        if not os.path.exists(config_file):
            self.stdout.write(self.style.ERROR(f"❌ Config file not found!"))
            return
            
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
                
            self.stdout.write(self.style.SUCCESS(f"✅ Config file loaded successfully"))
            
            # Check paths configuration
            paths = config.get('paths', [])
            if not paths:
                self.stdout.write(self.style.ERROR("❌ No paths configured for monitoring!"))
            else:
                self.stdout.write(f"Found {len(paths)} configured paths:")
                for i, path in enumerate(paths, 1):
                    exists = os.path.exists(path)
                    status = "✅ Exists" if exists else "❌ Not found"
                    self.stdout.write(f"  {i}. {path} - {status}")
                    
            # Check if monitor thread is running
            monitor_thread = get_monitor_thread()
            if monitor_thread and monitor_thread.is_alive():
                self.stdout.write(self.style.SUCCESS("✅ Monitor thread is running"))
                
                # Check what the monitor thread thinks it's monitoring
                if hasattr(monitor_thread, 'monitors') and monitor_thread.monitors:
                    active_monitor = monitor_thread.monitors[0]
                    if hasattr(active_monitor, 'paths'):
                        self.stdout.write("Currently monitoring paths:")
                        for path in active_monitor.paths:
                            self.stdout.write(f"  - {path}")
                    else:
                        self.stdout.write(self.style.WARNING("⚠️ Cannot determine actively monitored paths"))
                else:
                    self.stdout.write(self.style.WARNING("⚠️ Monitor thread has no active monitors"))
            else:
                self.stdout.write(self.style.ERROR("❌ Monitor thread is not running!"))
                
            # Check file analysis setup
            if 'monitoring' in config and 'change_detection' in config['monitoring']:
                self.stdout.write("\nChange detection configuration:")
                change_config = config['monitoring']['change_detection']
                for key, value in change_config.items():
                    self.stdout.write(f"  - {key}: {value}")
            else:
                self.stdout.write(self.style.WARNING("⚠️ No change detection configuration found"))
                
            # Check recent logs
            from myapp.models import FileChangeLog
            recent_logs = FileChangeLog.objects.order_by('-timestamp')[:5]
            
            self.stdout.write("\nRecent file events:")
            if recent_logs:
                for log in recent_logs:
                    self.stdout.write(f"  - {log.timestamp.strftime('%H:%M:%S')} - {log.change_type}: {log.file_path}")
            else:
                self.stdout.write("  No recent file events detected")
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Error checking monitor status: {e}"))