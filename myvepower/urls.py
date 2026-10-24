"""
URL configuration for myvepower project.
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('job_agent.urls')),             # Make Job Agent Dashboard the home page
    path('scraper/', include('scraper_app.urls')),   # Move old scraper to /scraper/
]
