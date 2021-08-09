import os

import django
from django.core.wsgi import get_wsgi_application

django.setup()

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'yatube.settings')

application = get_wsgi_application()
