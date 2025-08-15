"""
WSGI config for config project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os
from django.core.wsgi import get_wsgi_application
import logfire

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

logfire.configure()
logfire.instrument_django()      # Django 전반
logfire.instrument_sqlite3()     # DB 쿼리

application = get_wsgi_application()

application = logfire.instrument_wsgi(application, capture_headers=True)
