# from __future__ import absolute_import

# import os

# import celery

# from django.conf import settings


# # set the default Django settings module for the 'celery' program.
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'networkapi.settings')

# app = celery.Celery('networkapi', backend="amqp", broker='amqp://guest@localhost:5672//')


# # Using a string here means the worker will not have to
# # pickle the object when using Windows.
# app.config_from_object('django.conf:settings')

# # This allows you to load tasks from app/tasks.py files, they are
# # autodiscovered. Check @shared_app decorator to do that.
# app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
# app.conf.CELERY_TIMEZONE = 'UTC'
# app.conf.CELERY_SEND_EVENTS = True

# app.conf.update(
#     CELERY_ROUTES={}
# )


# # redis_host = os.environ.get('REDIS_HOST', 'localhost')
# # redis_port = os.environ.get('REDIS_PORT', '6379')
# # redis_password = os.environ.get('REDIS_PASSWORD', '')

# # auth_prefix = ''
# # if redis_password:
# #     auth_prefix = ':{}@'.format(redis_password)
# # redis_broker = "redis://{}{}:{}/0".format(auth_prefix, redis_host, redis_port)
# # redis_broker = "redis://:<password>@networkapi-01-145772292756.dev.redis.globoi.com:6379/0"
# # app = Celery('tasks', broker=redis_broker, backend=redis_broker)
# # app.conf.update(
# #     CELERY_TASK_SERIALIZER='json',
# #     CELERY_RESULT_SERIALIZER='json',
# #     CELERY_ACCEPT_CONTENT=['json'],
# # )
