from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='job_dashboard'),
    path('resume/', views.serve_resume_pdf, name='serve_resume'),
    path('api/refresh/', views.refresh_leads_api, name='api_refresh'),
    path('api/mark-applied/<int:lead_id>/', views.mark_applied_api, name='api_mark_applied'),
]
