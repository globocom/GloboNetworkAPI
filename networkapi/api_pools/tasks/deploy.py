# -*- coding: utf-8 -*-
from celery.utils.log import get_task_logger

from networkapi import celery_app
from networkapi.api_pools.facade.v3 import base as facade
from networkapi.api_pools.facade.v3 import deploy as facade_pool_deploy
from networkapi.api_pools.serializers import v3 as serializers
from networkapi.api_task.classes import BaseTask
from networkapi.distributedlock import LOCK_POOL
from networkapi.usuario.models import Usuario
from networkapi.util.geral import create_lock
from networkapi.util.geral import destroy_lock


logger = get_task_logger(__name__)


@celery_app.task(bind=True, base=BaseTask)
def deploy(self, pool_id, user_id):

    msg = {
        'object_type': 'pool',
        'action': 'deploy',
        'object_id': pool_id
    }
    self.update_state(
        state='PROGRESS',
        meta=msg
    )

    pool_obj = facade.get_pool_by_id(pool_id)
    pool_serializer = serializers.PoolV3Serializer(pool_obj)
    locks_list = create_lock([pool_id], LOCK_POOL)

    user = Usuario.objects.get(id=user_id)

    try:
        facade_pool_deploy.create_real_pool(
            [pool_serializer.data], user)

    except Exception, exception:
        msg['message'] = 'Pool {} was not deployed.'.format(pool_obj)
        msg['reason'] = str(exception)

        raise Exception(msg)

    else:
        msg['message'] = 'Pool {} was deployed with success.'.format(pool_obj)

        return msg

    finally:
        destroy_lock(locks_list)


@celery_app.task(bind=True, base=BaseTask)
def redeploy(self, pool_dict, user_id):

    pool_id = pool_dict.get('id')
    msg = {
        'object_type': 'pool',
        'action': 'redeploy',
        'object_id': pool_id
    }
    self.update_state(
        state='PROGRESS',
        meta=msg
    )

    pool_obj = facade.get_pool_by_id(pool_id)
    locks_list = create_lock([pool_id], LOCK_POOL)

    user = Usuario.objects.get(id=user_id)

    try:
        facade_pool_deploy.update_real_pool([pool_dict], user)

    except Exception, exception:
        msg['message'] = 'Pool {} was not redeployed.'.format(pool_obj)
        msg['reason'] = str(exception)

        raise Exception(msg)

    else:
        msg['message'] = 'Pool {} was redeployed with success.'.format(
            pool_obj)

        return msg

    finally:
        destroy_lock(locks_list)


@celery_app.task(bind=True, base=BaseTask)
def undeploy(self, pool_id, user_id):

    msg = {
        'object_type': 'pool',
        'action': 'undeploy',
        'object_id': pool_id
    }
    self.update_state(
        state='PROGRESS',
        meta=msg
    )

    pool_obj = facade.get_pool_by_id(pool_id)
    pool_serializer = serializers.PoolV3Serializer(pool_obj)
    locks_list = create_lock([pool_id], LOCK_POOL)

    user = Usuario.objects.get(id=user_id)

    try:
        facade_pool_deploy.delete_real_pool([pool_serializer.data], user)

    except Exception, exception:
        msg['message'] = 'Pool {} was not undeployed.'.format(pool_obj)
        msg['reason'] = str(exception)

        raise Exception(msg)

    else:
        msg['message'] = 'Pool {} was undeployed with success.'.format(
            pool_obj)

        return msg

    finally:
        destroy_lock(locks_list)
