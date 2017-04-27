# -*- coding: utf-8 -*-
from __future__ import absolute_import

import os

from celery import Celery
from django.conf import settings

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'networkapi.settings')

broker = 'amqp://{}/{}'.format(
    settings.BROKER_URL,
    os.getenv('NETWORKAPI_BROKER_VHOST', u'/')
)

app = Celery('networkapi', backend='amqp', broker=broker)

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
