# -*- coding: utf-8 -*-
from celery.utils.log import get_task_logger

from networkapi import celery_app
from networkapi.api_pools.facade.v3 import base as facade
from networkapi.api_pools.facade.v3 import deploy as facade_pool_deploy
from networkapi.api_pools.serializers import v3 as serializers
from networkapi.api_rest import exceptions as api_exceptions
from networkapi.distributedlock import LOCK_POOL
from networkapi.usuario.models import Usuario
from networkapi.util.geral import create_lock
from networkapi.util.geral import destroy_lock

logger = get_task_logger(__name__)


@celery_app.task(bind=True)
def deploy(self, pool_id, user_id):

    self.update_state(state='PROGRESS')

    pool = facade.get_pool_by_id(pool_id)
    pool_serializer = serializers.PoolV3Serializer(pool)
    locks_list = create_lock([pool_id], LOCK_POOL)

    user = Usuario.objects.get(id=user_id)

    try:
        facade_pool_deploy.create_real_pool(
            [pool_serializer.data], user)
    except Exception, exception:
        logger.exception(exception)
        raise api_exceptions.NetworkAPIException(exception)
    finally:
        destroy_lock(locks_list)

    return 'Pool {} was deployed with successs.'.format(pool)


@celery_app.task(bind=True)
def redeploy(self, pool_dict, user_id):

    self.update_state(state='PROGRESS')

    pool_id = pool_dict.get('id')
    locks_list = create_lock([pool_id], LOCK_POOL)

    user = Usuario.objects.get(id=user_id)
    try:
        pool = facade.get_pool_by_id(pool_id)
        facade_pool_deploy.update_real_pool([pool_dict], user)
    except Exception, exception:
        logger.exception(exception)
        raise api_exceptions.NetworkAPIException(exception)
    else:
        return 'Pool {} was redeployed with successs.'.format(pool)
    finally:
        destroy_lock(locks_list)


@celery_app.task(bind=True)
def undeploy(self, pool_id, user_id):

    self.update_state(state='PROGRESS')

    pool = facade.get_pool_by_id(pool_id)
    pool_serializer = serializers.PoolV3Serializer(pool)
    locks_list = create_lock([pool_id], LOCK_POOL)

    user = Usuario.objects.get(id=user_id)

    try:
        facade_pool_deploy.delete_real_pool(
            [pool_serializer.data], user)
    except Exception, exception:
        logger.exception(exception)
        raise api_exceptions.NetworkAPIException(exception)
    finally:
        destroy_lock(locks_list)

    return 'Pool {} was redeployed with successs.'.format(pool)
