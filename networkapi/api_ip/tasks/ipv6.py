# -*- coding: utf-8 -*-
from celery.utils.log import get_task_logger

from networkapi import celery_app
from networkapi.api_pools import facade
from networkapi.api_rest import exceptions as api_exceptions
from networkapi.usuario.models import Usuario

logger = get_task_logger(__name__)


@celery_app.task(bind=True)
def create_ipv6(self, ip_dict, user_id):

    self.update_state(state='PROGRESS')

    user = Usuario.objects.get(id=user_id)

    try:

        ip = facade.create_ipv6(ip_dict, user)

    except Exception, exception:
        logger.exception(exception)
        raise api_exceptions.NetworkAPIException(exception)

    else:
        msg = {
            'object_type': 'Ipv6',
            'object_id': ip.id,
            'message': 'Ipv6 {} was allocated with success.'.format(ip)
        }
        return msg


@celery_app.task(bind=True)
def update_ipv6(self, ip_dict, user_id):

    self.update_state(state='PROGRESS')

    user = Usuario.objects.get(id=user_id)

    try:

        ip = facade.update_ipv6(ip_dict, user)

    except Exception, exception:
        logger.exception(exception)
        raise api_exceptions.NetworkAPIException(exception)

    else:
        msg = {
            'object_type': 'Ipv6',
            'object_id': ip.id,
            'message': 'Ipv6 {} was updated with success.'.format(ip)
        }
        return msg


@celery_app.task(bind=True)
def delete_ipv6(self, ip_id):

    self.update_state(state='PROGRESS')

    try:

        ip_obj = facade.get_ipv6_by_id(ip_id)
        ip_formated = ip_obj.ip_formated
        facade.delete_ipv6(ip_id)

    except Exception, exception:
        logger.exception(exception)
        raise api_exceptions.NetworkAPIException(exception)

    else:
        msg = {
            'object_type': 'Ipv6',
            'object_id': ip_id,
            'message': 'Ipv6 {} was deallocated with success.'.format(ip_formated)
        }
        return msg
