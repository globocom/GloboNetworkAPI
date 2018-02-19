# -*- coding: utf-8 -*-

from networkapi import settings
from networkapi import celery_app
from networkapi.api_task.classes import BaseTask


@celery_app.task(bind=True, base=BaseTask, serializer='pickle')
def async_add_flow(self, plugins, user_id, data):
    """ Asynchronous flows insertion into environment equipment """

    for plugin in plugins:
        if plugin is not None:
            plugin.add_flow(data=data)


@celery_app.task(bind=True, base=BaseTask, serializer='pickle')
def async_flush_environment(self, plugins, user_id, data):
    """ Asynchronous flush and restore of flows of an environment """

    for plugin in plugins:
        if plugin is not None:
            plugin.update_all_flows(data=data)
