from django.apps import AppConfig


class MyappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'myapp'

    def ready(self):
        from myapp.file_monitor.watcher import start_monitor_in_thread
        start_monitor_in_thread()
