from django.core.management.base import BaseCommand
from file_management.file_monitor.watcher import stop_monitor, ensure_single_monitor
import time
import os
import json
from django.conf import settings

class Command(BaseCommand):
    help = 'Restart the file monitoring system'

    def handle(self, *args, **options):
        self.stdout.write("Stopping existing file monitor...")
        if stop_monitor():
            self.stdout.write(self.style.SUCCESS("✅ Existing monitor stopped"))
        else:
            self.stdout.write(self.style.WARNING("No active monitor to stop"))
            
        # Wait a moment for cleanup
        time.sleep(2)
        
        # Load paths from config
        config_file = os.path.join(settings.BASE_DIR, 'monitor_config.json')
        paths = []
        
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    config = json.load(f)
                    paths = config.get('paths', [])
                    self.stdout.write(f"Loaded {len(paths)} paths from config")
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error loading config: {e}"))
        
        # Start a new monitor
        self.stdout.write("Starting new file monitor...")
        monitor = ensure_single_monitor(paths)
        
        if monitor and monitor.is_alive():
            self.stdout.write(self.style.SUCCESS("✅ New monitor started successfully"))
            
            # Show what's being monitored
            if hasattr(monitor, 'paths'):
                self.stdout.write("Monitoring paths:")
                for path in monitor.paths:
                    self.stdout.write(f"  - {path}")
        else:
            self.stdout.write(self.style.ERROR("❌ Failed to start new monitor"))