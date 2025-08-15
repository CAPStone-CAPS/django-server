"""
ASGI config for config project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application
import logfire

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

logfire.configure()
logfire.instrument_django()      # Django 전반
logfire.instrument_sqlite3()     # DB 쿼리

application = get_asgi_application()

application = logfire.instrument_asgi(application, capture_headers=True)