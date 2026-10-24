"""
WSGI config for myvepower project on Vercel and production.
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myvepower.settings')

# Run migrations automatically if running on Vercel temporary storage
if os.environ.get('VERCEL'):
    try:
        from django.core.management import call_command
        import django
        django.setup()
        call_command('migrate', interactive=False)
    except Exception as e:
        print(f"Vercel migration notice: {e}")

application = get_wsgi_application()
app = application
