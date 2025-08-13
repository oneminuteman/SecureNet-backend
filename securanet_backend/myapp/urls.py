from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'file-logs', views.FileChangeLogListView, basename='file-logs')

urlpatterns = [
    # Existing paths
    path('', include(router.urls)),
    path('monitored-directories/', views.get_monitored_directories, name='monitored-directories'),
    path('statistics/', views.get_statistics, name='statistics'),
    
    # Monitor control endpoints
    path('monitor/status/', views.monitor_status, name='monitor_status'),
    path('monitor/start/', views.start_monitor, name='start_monitor'),
    path('monitor/stop/', views.stop_monitor_view, name='stop_monitor'),
    path('monitor/restart/', views.restart_monitor, name='restart_monitor'),
    path('monitor/update-directories/', views.update_directories, name='update_directories'),
    path('monitor/run-scan/', views.run_scan, name='run_scan'),
    path('monitor/set-scan-interval/', views.set_scan_interval, name='set_scan_interval'),
]