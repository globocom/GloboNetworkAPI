# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

import logging

from networkapi import celery_app
from networkapi.api_rest import exceptions as api_exceptions
from networkapi.api_vip_request.facade import v3 as facade
from networkapi.api_vip_request.serializers.v3 import VipRequestV3Serializer
from networkapi.distributedlock import LOCK_VIP
from networkapi.settings import SPECS
from networkapi.util.geral import create_lock
from networkapi.util.geral import destroy_lock
from networkapi.util.json_validate import json_validate
from networkapi.util.json_validate import verify_ports_vip
logger = logging.getLogger(__name__)


@celery_app.task
def deploy(vip_request_ids, user):

    vips = facade.get_vip_request_by_ids(vip_request_ids)
    vip_serializer = VipRequestV3Serializer(
        vips, many=True, include=('ports__identifier',))

    locks_list = create_lock(vip_serializer.data, LOCK_VIP)
    try:
        response = facade.create_real_vip_request(
            vip_serializer.data, user)
    except Exception, exception:
        logger.exception(exception)
        raise api_exceptions.NetworkAPIException(exception)
    finally:
        destroy_lock(locks_list)

    return response


@celery_app.task
def undeploy(vip_request_ids, user):

    vips = facade.get_vip_request_by_ids(vip_request_ids)
    vip_serializer = VipRequestV3Serializer(
        vips, many=True, include=('ports__identifier',))

    locks_list = create_lock(vip_serializer.data, LOCK_VIP)
    try:
        response = facade.delete_real_vip_request(
            vip_serializer.data, user)
    except Exception, exception:
        logger.exception(exception)
        raise api_exceptions.NetworkAPIException(exception)
    finally:
        destroy_lock(locks_list)

    return response


@celery_app.task
def redeploy(vips, user):

    json_validate(SPECS.get('vip_request_put')).validate(vips)
    locks_list = create_lock(vips.get('vips'), LOCK_VIP)
    verify_ports_vip(vips)
    try:
        response = facade.update_real_vip_request(
            vips['vips'], user)
    except Exception, exception:
        logger.exception(exception)
        raise api_exceptions.NetworkAPIException(exception)
    finally:
        destroy_lock(locks_list)

    return response
