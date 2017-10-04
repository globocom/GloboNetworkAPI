# -*- coding: utf-8 -*-

from networkapi import settings
from networkapi import celery_app
from networkapi.api_task.classes import BaseTask


@celery_app.task(bind=True, base=BaseTask, serializer='pickle')
def async_add_flow(self, plugin, user_id, data):
    """ Asynchronous flows insertion into environment equipment """

    return plugin.add_flow(data=data)


@celery_app.task(bind=True, base=BaseTask, serializer='pickle')
def async_flush_environment(self, plugin, user_id, data):
    """ Asynchronous flush and restore of flows of an environment """

    if settings.NETWORKAPI_ODL_NEW_FLUSH=="1":
        plugin.update_all_flows(data=data)
    else:
        plugin.flush_flows()
        return plugin.add_flow(data=data)
