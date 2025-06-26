import time
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from decouple import config
from myapp.models import FileChangeLog  # create this model next!
from myapp.file_monitor.detector import is_suspicious_change

class MonitorHandler(FileSystemEventHandler):
    def on_created(self, event):
        suspicious = is_suspicious_change(event.src_path, 'created')
        FileChangeLog.objects.create(file_path=event.src_path, change_type='created', suspicious=suspicious)

    def on_deleted(self, event):
        suspicious = is_suspicious_change(event.src_path, 'deleted')
        FileChangeLog.objects.create(file_path=event.src_path, change_type='deleted', suspicious=suspicious)

    def on_modified(self, event):
        suspicious = is_suspicious_change(event.src_path, 'modified')
        FileChangeLog.objects.create(file_path=event.src_path, change_type='modified', suspicious=suspicious)

    def on_moved(self, event):
        suspicious = is_suspicious_change(event.dest_path, 'renamed')
        FileChangeLog.objects.create(file_path=event.dest_path, change_type='renamed', suspicious=suspicious)

def start_monitor():
    folder_path = config('WATCH_FOLDER', default=None)
    if not folder_path:
        print("WATCH_FOLDER not set.")
        return

    event_handler = MonitorHandler()
    observer = Observer()
    observer.schedule(event_handler, path=folder_path, recursive=True)
    observer.start()
    print(f"Started monitoring folder: {folder_path}")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

def start_monitor_in_thread():
    thread = threading.Thread(target=start_monitor, daemon=True)
    thread.start()
