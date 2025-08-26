from django.urls import path
from .views import (
    home_view,
    capture_view,
    compare_sites_view,
    detect_view,
    recent_scans,
    test_whoisxml,
    get_csrf_token,
    signup_view,
    login_view,
    logout_view,
)

urlpatterns = [
     path("auth/csrf/", get_csrf_token),
    path("auth/signup/", signup_view),
    path("auth/login/", login_view),
    path("auth/logout/", logout_view),
    path('', home_view),
    path('capture/', capture_view),
    path('compare/', compare_sites_view),
    path('detect/', detect_view),
    path('recent-scans/', recent_scans),
    path('test-whoisxml/', test_whoisxml),  # Optional
]


