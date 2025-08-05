from django.core.management.base import BaseCommand
from myapp.file_monitor.watcher import get_monitor_thread

class Command(BaseCommand):
    help = 'Immediately run a file scan instead of waiting for the scheduled scan'

    def add_arguments(self, parser):
        parser.add_argument(
            '--path',
            help='Optional specific path to scan (defaults to all monitored paths)',
        )
        
        parser.add_argument(
            '--quick',
            action='store_true',
            help='Do a quick scan (faster but less thorough)',
        )

    def handle(self, *args, **options):
        monitor_thread = get_monitor_thread()
        
        if not monitor_thread:
            self.stdout.write(self.style.ERROR('❌ No active file monitor found'))
            return
            
        path = options.get('path')
        quick = options.get('quick', False)
        
        self.stdout.write(f"Starting {'quick ' if quick else ''}file scan now...")
        
        if path:
            self.stdout.write(f"Scanning specific path: {path}")
            # Call a custom method that scans just this path
            if hasattr(monitor_thread, 'scan_specific_path'):
                monitor_thread.scan_specific_path(path, quick=quick)
            else:
                self.stdout.write(self.style.WARNING('⚠️ Specific path scanning not supported by this monitor'))
                monitor_thread.run_full_scan()
        else:
            # Run the regular full scan
            monitor_thread.run_full_scan(quick=quick)
            
        self.stdout.write(self.style.SUCCESS('✅ Scan initiated successfully'))
        self.stdout.write('Check the log page in a moment to see any detected changes')