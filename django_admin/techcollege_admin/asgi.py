"""
ASGI config for techcollege_admin project.
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'techcollege_admin.settings')

application = get_asgi_application()
