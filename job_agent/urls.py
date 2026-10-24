from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='job_dashboard'),
    path('api/fetch/', views.trigger_fetch_companies, name='api_fetch'),
    path('api/send/', views.trigger_send_emails, name='api_send'),
    path('api/status/', views.api_task_status, name='api_status'),
]
