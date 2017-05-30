# -*- coding: utf-8 -*-
from networkapi import celery_app
from networkapi.queue_tools.rabbitmq import QueueManager
from networkapi.usuario.models import Usuario


class BaseTask(celery_app.Task):

    def after_return(self, status, retval, task_id, args, kwargs, einfo):

        user = Usuario.get_by_pk(args[1])

        task = celery_app.AsyncResult(task_id)
        if status == 'FAILURE':
            result = task.result.exc_message
        else:
            result = task.result

        queue_name = 'tasks.%s' % user.user.lower()
        routing_key = '%s.%s' % (queue_name, task_id)
        queue_manager = QueueManager(broker_vhost='tasks',
                                     queue_name=queue_name,
                                     exchange_name=queue_name,
                                     routing_key=routing_key)
        queue_manager.append({
            'task_id': task_id,
            'status': status,
            'result': result
        })
        queue_manager.send()
