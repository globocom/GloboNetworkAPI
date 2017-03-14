# -*- coding: utf-8 -*-
import logging

from networkapi import celery_app
from networkapi.api_pools.facade.v3 import base as facade
from networkapi.api_pools.facade.v3 import deploy as facade_pool_deploy
from networkapi.api_pools.serializers import v3 as serializers
from networkapi.api_rest import exceptions as api_exceptions
from networkapi.distributedlock import LOCK_POOL
from networkapi.settings import SPECS
from networkapi.util.geral import create_lock
from networkapi.util.geral import destroy_lock
from networkapi.util.json_validate import json_validate
from networkapi.util.json_validate import verify_ports
logger = logging.getLogger(__name__)


@celery_app.task
def deploy(pool_ids, user):

    pools = facade.get_pool_by_ids(pool_ids)
    pool_serializer = serializers.PoolV3Serializer(pools, many=True)
    locks_list = create_lock(pool_serializer.data, LOCK_POOL)

    try:
        response = facade_pool_deploy.create_real_pool(
            pool_serializer.data, user)
    except Exception, exception:
        logger.exception(exception)
        raise api_exceptions.NetworkAPIException(exception)
    finally:
        destroy_lock(locks_list)

    return response


@celery_app.task
def redeploy(pools, user):

    json_validate(SPECS.get('pool_put')).validate(pools)
    verify_ports(pools)
    locks_list = create_lock(pools.get('server_pools'), LOCK_POOL)

    try:
        response = facade_pool_deploy.update_real_pool(pools, user)
    except Exception, exception:
        logger.exception(exception)
        raise api_exceptions.NetworkAPIException(exception)
    finally:
        destroy_lock(locks_list)

    return response


@celery_app.task
def undeploy(pool_ids, user):

    pools = facade.get_pool_by_ids(pool_ids)
    pool_serializer = serializers.PoolV3Serializer(pools, many=True)
    locks_list = create_lock(pool_serializer.data, LOCK_POOL)

    try:
        response = facade_pool_deploy.delete_real_pool(
            pool_serializer.data, user)
    except Exception, exception:
        logger.exception(exception)
        raise api_exceptions.NetworkAPIException(exception)
    finally:
        destroy_lock(locks_list)
    return response
