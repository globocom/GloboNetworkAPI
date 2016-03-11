# -*- coding:utf-8 -*-
from networkapi.api_pools import facade
from networkapi.api_task.facade import BaseTask
from networkapi.celeryconf import app
from util import state_change

app.conf.CELERY_ROUTES.update({
    'networkapi.api_pools.tasks.create_real_pool': {'queue': 'real_pool', 'desc': 'Criar Real Pool'},
    'networkapi.api_pools.tasks.update_real_pool': {'queue': 'real_pool', 'desc': 'Atualizar Real Pool'},
    'networkapi.api_pools.tasks.delete_real_pool': {'queue': 'real_pool', 'desc': 'Deletar Real Pool'},
})


@app.task(base=BaseTask, bind=True)
@state_change
def create_real_pool(self, pools):
    locks_list = facade.create_lock(pools)
    try:
        facade.create_real_pool(pools)
    finally:
        facade.destroy_lock(locks_list)

    return 'create_real_pool: %s' % locks_list


@app.task(base=BaseTask, bind=True)
@state_change
def update_real_pool(pools):

    locks_list = facade.create_lock(pools)
    try:
        facade.update_real_pool(pools)
    finally:
        facade.destroy_lock(locks_list)

    return 'update_real_pool: %s' % locks_list


@app.task(base=BaseTask, bind=True)
@state_change
def delete_real_pool(pools):

    locks_list = facade.create_lock(pools)
    try:
        facade.delete_real_pool(pools)
    finally:
        facade.destroy_lock(locks_list)

    return 'delete_real_pool: %s' % locks_list
