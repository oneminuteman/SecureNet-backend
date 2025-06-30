import time
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from decouple import config
from myapp.file_monitor.detector import is_suspicious_change
from myapp.file_monitor.file_monitor import log_file_change  # ✅ fix import

class MonitorHandler(FileSystemEventHandler):
    def on_created(self, event):
        file_path = event.src_path
        change_type = 'created'
        suspicious = is_suspicious_change(file_path, change_type)
        log_file_change(file_path, change_type)

    def on_deleted(self, event):
        file_path = event.src_path
        change_type = 'deleted'
        suspicious = is_suspicious_change(file_path, change_type)
        log_file_change(file_path, change_type)

    def on_modified(self, event):
        file_path = event.src_path
        change_type = 'modified'
        suspicious = is_suspicious_change(file_path, change_type)
        log_file_change(file_path, change_type)

    def on_moved(self, event):
        file_path = event.dest_path
        change_type = 'renamed'
        suspicious = is_suspicious_change(file_path, change_type)
        log_file_change(file_path, change_type)

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
