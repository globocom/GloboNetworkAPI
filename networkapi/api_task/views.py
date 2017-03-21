# -*- coding: utf-8 -*-
from rest_framework import status
from rest_framework.response import Response

from networkapi import celery_app
from networkapi.util.classes import CustomAPIView


class TaskView(CustomAPIView):

    def get(self, request, *args, **kwargs):
        """
        Query Celery for task status based on its taskid/jobid

        Celery status can be one of:
        PENDING - Job not yet run or unknown status
        PROGRESS - Job is currently running
        SUCCESS - Job completed successfully
        FAILURE - Job failed
        REVOKED - Job get canceled
        """

        task_id = kwargs.get('task_id')
        task = celery_app.AsyncResult(task_id)

        if task.state == 'PENDING':
            payload = dict(task_id=task.id, status=task.state)
        elif task.state == 'SUCCESS':
            payload = dict(task_id=task.id, status=task.state,
                           result=task.result)
        elif task.state == 'PROGRESS':
            payload = dict(task_id=task.id, status=task.state,
                           result=task.result)
        elif task.state == 'FAILURE':
            payload = dict(task_id=task.id, status=task.state,
                           result=task.result)
        else:
            payload = dict(task_id=task.id, status=task.state,
                           result=task.result)

        return Response(payload, status=status.HTTP_200_OK)
