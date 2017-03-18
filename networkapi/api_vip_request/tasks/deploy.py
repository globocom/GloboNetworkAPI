# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

import logging

from networkapi import celery_app
from networkapi.api_rest import exceptions as api_exceptions
from networkapi.api_vip_request.facade import v3 as facade
from networkapi.api_vip_request.serializers.v3 import VipRequestV3Serializer
from networkapi.distributedlock import LOCK_VIP
from networkapi.usuario.models import Usuario
from networkapi.util.geral import create_lock
from networkapi.util.geral import destroy_lock

logger = logging.getLogger(__name__)


@celery_app.task(bind=True)
def deploy(self, vip_id, user_id):

    self.update_state(state='PROGRESS')

    vip = facade.get_vip_request_by_id(vip_id)
    vip_serializer = VipRequestV3Serializer(vip,
                                            include=('ports__identifier',))
    locks_list = create_lock([vip_id], LOCK_VIP)

    user = Usuario.objects.get(id=user_id)

    try:
        vip = facade.get_vip_request_by_id(vip_id)
        facade.create_real_vip_request([vip_serializer.data], user)

    except Exception, exception:
        logger.exception(exception)
        raise api_exceptions.NetworkAPIException(exception)

    else:
        msg = {
            'object_type': 'Vip Request',
            'object_id': vip_id,
            'message': 'Vip Request {} was deployed with success.'.format(vip)
        }
        return msg

    finally:
        destroy_lock(locks_list)


@celery_app.task(bind=True)
def undeploy(self, vip_id, user_id):

    self.update_state(state='PROGRESS')

    vip = facade.get_vip_request_by_id(vip_id)
    vip_serializer = VipRequestV3Serializer(vip,
                                            include=('ports__identifier',))
    locks_list = create_lock([vip_id], LOCK_VIP)

    user = Usuario.objects.get(id=user_id)

    try:
        vip = facade.get_vip_request_by_id(vip_id)
        facade.delete_real_vip_request([vip_serializer.data], user)

    except Exception, exception:
        logger.exception(exception)
        raise api_exceptions.NetworkAPIException(exception)

    else:
        msg = {
            'object_type': 'Vip Request',
            'object_id': vip_id,
            'message': 'Vip Request {} was undeployed with success.'.format(
                vip)
        }
        return msg

    finally:
        destroy_lock(locks_list)


@celery_app.task(bind=True)
def redeploy(self, vip_dict, user_id):

    self.update_state(state='PROGRESS')

    vip_id = vip_dict.get('id')
    locks_list = create_lock([vip_id], LOCK_VIP)

    user = Usuario.objects.get(id=user_id)

    try:
        vip = facade.get_vip_request_by_id(vip_id)
        facade.update_real_vip_request([vip_dict], user)

    except Exception, exception:
        logger.exception(exception)
        raise api_exceptions.NetworkAPIException(exception)

    else:
        msg = {
            'object_type': 'Vip Request',
            'object_id': vip_id,
            'message': 'Vip Request {} was redeployed with success.'.format(
                vip)
        }
        return msg

    finally:
        destroy_lock(locks_list)
