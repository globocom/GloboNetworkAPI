# -*- coding: utf-8 -*-

from networkapi import celery_app
from networkapi.api_task.classes import BaseTask


@celery_app.task(bind=True, base=BaseTask, serializer='pickle')
def async_add_flow(self, plugin, data):
    return plugin.add_flow(data=data)
