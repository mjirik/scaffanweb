"""
WSGI config for scaffanweb project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'scaffanweb.settings')

print("we are in python now")
application = get_wsgi_application()
print("after get_wsgi_application()")
