from django.core.management.base import BaseCommand
import time
import threading
import logging
import os
import argparse
from datetime import datetime, timedelta
from pathlib import Path

from file_management.file_monitor.watcher import ensure_single_monitor, get_monitor_thread

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Run the file monitoring system with efficiency optimizations'

    def add_arguments(self, parser):
        parser.add_argument(
            '--delay-full-scan',
            type=int,
            default=2,
            help='Delay full system scan by specified minutes after startup'
        )
        parser.add_argument(
            '--lightweight-startup',
            action='store_true',
            help='Start with lightweight monitoring and defer intensive operations'
        )
        parser.add_argument(
            '--scan-critical-only',
            action='store_true',
            help='Only scan critical directories on startup'
        )

    def create_file_state_cache_dir(self):
        """Create file state cache directory if it doesn't exist"""
        cache_dir = Path('./file_state_cache')
        if not cache_dir.exists():
            try:
                cache_dir.mkdir(parents=True, exist_ok=True)
                self.stdout.write(self.style.SUCCESS(f"Created cache directory: {cache_dir}"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Failed to create cache directory: {e}"))

    def schedule_full_scan(self, delay_minutes):
        """Schedule a full scan after the specified delay"""
        self.stdout.write(f"Scheduling full system scan in {delay_minutes} minutes...")
        
        def run_full_scan():
            # Sleep for the specified delay
            time.sleep(delay_minutes * 60)
            
            # Log the start of the full scan
            self.stdout.write(self.style.SUCCESS(
                f"Starting full system scan at {datetime.now().strftime('%H:%M:%S')}"
            ))
            
            # Run the full scan
            monitor_thread = get_monitor_thread()
            if monitor_thread and hasattr(monitor_thread, 'run_full_scan'):
                monitor_thread.run_full_scan()
            else:
                self.stdout.write(self.style.WARNING(
                    "Full scan not supported by current monitor implementation"
                ))
        
        # Start the delayed scan in a separate thread
        scan_thread = threading.Thread(target=run_full_scan, daemon=True)
        scan_thread.start()
        
        return scan_thread

    def handle(self, *args, **options):
        delay_minutes = options['delay_full_scan']
        lightweight_startup = options['lightweight_startup']
        scan_critical_only = options['scan_critical_only']
        
        # Ensure the file state cache directory exists
        self.create_file_state_cache_dir()
        
        # Set environment variables for the monitor
        if lightweight_startup:
            os.environ['MONITOR_LIGHTWEIGHT_STARTUP'] = 'true'
        if scan_critical_only:
            os.environ['MONITOR_SCAN_CRITICAL_ONLY'] = 'true'
            
        # Start the monitor with appropriate options
        monitor_thread = ensure_single_monitor()
        
        if monitor_thread and monitor_thread.is_alive():
            self.stdout.write(self.style.SUCCESS("File monitoring started successfully"))
            
            # Schedule the full scan
            scan_thread = self.schedule_full_scan(delay_minutes)
            
            # Wait for the monitor thread
            try:
                while monitor_thread.is_alive():
                    time.sleep(1)
            except KeyboardInterrupt:
                self.stdout.write(self.style.WARNING("Shutting down monitor..."))
                # Your monitor should handle graceful shutdown
        else:
            self.stdout.write(self.style.ERROR("Failed to start file monitor"))