from django.shortcuts import render
from .models import Provider

def dashboard_view(request):
    providers = Provider.objects.prefetch_related('games').all()
    return render(request, 'scraper_app/dashboard.html', {'providers': providers})
