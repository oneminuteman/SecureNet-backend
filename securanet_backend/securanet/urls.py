from django.urls import path
from . import views

urlpatterns = [
     path('', views.home_view, name='home'),
    path('capture/', views.capture_view, name='capture_view'),
    path('compare/', views.compare_sites_view, name='compare_sites_view'),
    path('detect/', views.detect_view, name='detect_clone'),
]

