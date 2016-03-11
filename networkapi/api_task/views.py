# -*- coding:utf-8 -*-
import logging

from celery.task.control import revoke

from networkapi.api_rest import exceptions as api_exceptions
from networkapi.api_task import exceptions as task_exceptions
from networkapi.api_task import facade

from rest_framework import status
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

log = logging.getLogger(__name__)


@permission_classes((IsAuthenticated, ))
class TaskListView(APIView):

    def get(self, request, *args, **kwargs):
        log.info("View:%s, method:%s" % (type(self).__name__, request.method))
        log.debug('Data send: %s' % request.DATA)
        log.debug('Url params: %s' % kwargs)
        try:
            key = '%s:%s' % ('tasks', request.user.id)
            tasks_cache = facade.get_tasks_cache(key)

            return Response(tasks_cache, status.HTTP_200_OK)

        except Exception, exception:
            log.error(exception)
            raise api_exceptions.NetworkAPIException(exception)


@permission_classes((IsAuthenticated, ))
class TaskView(APIView):

    def get(self, request, *args, **kwargs):
        log.info("View:%s, method:%s" % (type(self).__name__, request.method))
        log.debug('Data send: %s' % request.DATA)
        log.debug('Url params: %s' % kwargs)
        try:
            task_id = kwargs["task_id"]
            key = '%s:%s' % ('tasks', request.user.id)
            task = facade.get_task_cache(key, task_id)

            return Response(task, status.HTTP_200_OK)

        except Exception, exception:
            log.error(exception)
            raise api_exceptions.NetworkAPIException(exception)

    def delete(self, request, *args, **kwargs):
        log.info("View:%s, method:%s" % (type(self).__name__, request.method))
        log.debug('Data send: %s' % request.DATA)
        log.debug('Url params: %s' % kwargs)
        try:
            task_id = kwargs["task_id"]
            key = '%s:%s' % ('tasks', request.user.id)
            task = facade.get_task_cache(key, task_id)
            if task['state'] == 'PENDING':
                task['state'] = 'REVOKING'
                revoke(task_id, terminate=True)
                facade.update_task_cache(task, key)
                return Response({}, status.HTTP_200_OK)
            else:
                raise task_exceptions.TaskReadyException()

        except Exception, exception:
            log.error(exception)
            raise api_exceptions.NetworkAPIException(exception)