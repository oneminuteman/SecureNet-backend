from django.core.management.base import BaseCommand
from myapp.file_monitor.watcher import FileMonitor
import time
import os
from django.conf import settings

class Command(BaseCommand):
    help = 'Starts the file monitoring system'

    def add_arguments(self, parser):
        parser.add_argument(
            '--path',
            type=str,
            default=settings.WATCH_FOLDER,
            help='Path to monitor'
        )

    def handle(self, *args, **options):
        path_to_watch = options['path']
        
        if not os.path.exists(path_to_watch):
            self.stderr.write(self.style.ERROR(f'Path does not exist: {path_to_watch}'))
            return

        self.stdout.write(self.style.SUCCESS(f'Starting file monitor on: {path_to_watch}'))
        
        monitor = FileMonitor(path_to_watch)
        
        try:
            monitor.start()
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            monitor.stop()
            self.stdout.write(self.style.SUCCESS('Monitor stopped'))