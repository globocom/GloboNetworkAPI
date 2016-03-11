# -*- coding:utf-8 -*-
import json
import logging
import time

from django.core.cache import cache

from networkapi.celeryconf import app, celery


class BaseTask(celery.Task):
    abstract = True

    def __call__(self, *args, **kwargs):
        t = self.app.AsyncResult(self.request.id)
        print('TASK CALL: %s' % t.state)
        return super(BaseTask, self).__call__(*args, **kwargs)

    def after_return(self, *args, **kwargs):
        t = self.app.AsyncResult(self.request.id)
        print('TASK RETURN: %s' % t.state)


def set_task_cache(task, key):
    value = {
        task.id: {
            'desc': task.app.conf.CELERY_ROUTES[task.task_name]['desc'],
            'state': task.state,
            'id': task.id,
            'time': time.time()
        }
    }
    if not cache.get(key):
        tasks_cache = dict()
        cache.set(key, json.dumps(tasks_cache))
    else:
        values = cache.get(key)
        tasks_cache = json.loads(values)

    tasks_cache.update(value)
    cache.set(key, json.dumps(tasks_cache))

    return value[task.id]


def update_task_cache(task, key):

    if not cache.get(key):
        tasks_cache = dict()
        cache.set(key, json.dumps(tasks_cache))
    else:
        values = cache.get(key)
        tasks_cache = json.loads(values)

    tasks_cache[task['id']] = task
    cache.set(key, json.dumps(tasks_cache))

    return task


def get_tasks_cache(key):
    tasks_cache = cache.get(key) or []
    new_tasks_cache = dict()
    tasks = list()
    if tasks_cache:
        tasks_cache = json.loads(tasks_cache)
        for i, task_item in enumerate(tasks_cache):

            task = app.AsyncResult(task_item)
            old_state = tasks_cache[task_item]['state']
            new_state = task.state

            if new_state == 'PENDING' and old_state == 'REVOKING':
                new_state = 'REVOKING'

            tasks_cache[task_item]['state'] = new_state

            tasks.append(tasks_cache[task_item])

            if not (new_state == old_state and new_state in ['SUCCESS', 'FAILURE', 'REVOKED'] and tasks_cache[task_item]['time'] >= time.time() + 300):

                new_tasks_cache[task_item] = tasks_cache.get(task_item)

        cache.set(key, json.dumps(new_tasks_cache))

    return sorted(tasks, key=lambda k: k['time'], reverse=True)


# def get_task_cache(key, task_id):
#     return app.AsyncResult(task_id)
#     # tasks_cache = cache.get(key) or []
#     # if tasks_cache:
#     #     tasks_json = json.loads(tasks_cache)
#     #     if tasks_json.get(task_id):
#     #         task = app.AsyncResult(task_id)
#     #         return task

#     # return None

def get_task_cache(key, task_id):
    tasks_cache = cache.get(key) or []
    if tasks_cache:
        tasks_json = json.loads(tasks_cache)
        if tasks_json.get(task_id):
            task_cache = tasks_json.get(task_id)
            task = app.AsyncResult(task_id)
            task_cache['state'] = task.state
            return task_cache
    return None
