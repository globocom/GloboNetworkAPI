import os
import sys

APP_DIR = os.path.realpath(__file__ + './')

sys.path.insert(0, APP_DIR)

os.environ['PYTHON_EGG_CACHE'] = os.path.join(APP_DIR, '.egg-cache')
os.environ['DJANGO_SETTINGS_MODULE'] = 'networkapi.settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
