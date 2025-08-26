from django.core.management.base import BaseCommand
from file_management.file_monitor.watcher import get_monitor_thread
import time

class Command(BaseCommand):
    help = 'Start a file system scan immediately'

    def add_arguments(self, parser):
        parser.add_argument(
            '--path',
            type=str,
            help='Specific path to scan (optional)',
        )

    def handle(self, *args, **options):
        # Get the monitor thread
        monitor_thread = get_monitor_thread()
        
        if not monitor_thread or not monitor_thread.is_alive():
            self.stdout.write(self.style.ERROR("❌ Monitor thread is not running. Start the server first."))
            return
        
        # Start the scan
        self.stdout.write(self.style.WARNING("Starting file system scan..."))
        start_time = time.time()
        
        # Run the scan
        monitor_thread.run_full_scan()
        
        self.stdout.write(self.style.SUCCESS(f"✅ Scan initiated successfully"))
        self.stdout.write(f"The scan is running in the background. Check logs for progress.")