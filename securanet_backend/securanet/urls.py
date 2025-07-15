from django.urls import path
from .views import (
    home_view,
    capture_view,
    compare_sites_view,
    detect_view,
    recent_scans,
    test_whoisxml,
)

urlpatterns = [
    path('', home_view),
    path('capture/', capture_view),
    path('compare/', compare_sites_view),
    path('detect/', detect_view),
    path('recent-scans/', recent_scans),
    path('test-whoisxml/', test_whoisxml),  # Optional
]


