from django.urls import path
from .views import *

urlpatterns = [
    path('phishinglogs/', phishing_log_list_create, name='phishinglogs-list-create'),
]
