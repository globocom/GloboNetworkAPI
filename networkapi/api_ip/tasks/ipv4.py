# -*- coding: utf-8 -*-
from celery.utils.log import get_task_logger

from networkapi import celery_app
from networkapi.api_ip import facade
from networkapi.api_rest import exceptions as api_exceptions
from networkapi.usuario.models import Usuario

logger = get_task_logger(__name__)


@celery_app.task(bind=True)
def create_ipv4(self, ip_dict, user_id):

    self.update_state(state='PROGRESS')

    user = Usuario.objects.get(id=user_id)

    try:

        ip = facade.create_ipv4(ip_dict, user)

    except Exception, exception:
        logger.exception(exception)
        raise api_exceptions.NetworkAPIException(exception)

    else:
        msg = {
            'object_type': 'Ipv4',
            'object_id': ip.id,
            'message': 'Ipv4 {} was allocated with success.'.format(ip)
        }
        return msg


@celery_app.task(bind=True)
def update_ipv4(self, ip_dict, user_id):

    self.update_state(state='PROGRESS')

    user = Usuario.objects.get(id=user_id)

    try:

        ip = facade.update_ipv4(ip_dict, user)

    except Exception, exception:
        logger.exception(exception)
        raise api_exceptions.NetworkAPIException(exception)

    else:
        msg = {
            'object_type': 'Ipv4',
            'object_id': ip.id,
            'message': 'Ipv4 {} was updated with success.'.format(ip)
        }
        return msg


@celery_app.task(bind=True)
def delete_ipv4(self, ip_id):

    self.update_state(state='PROGRESS')

    try:

        ip_obj = facade.get_ipv4_by_id(ip_id)
        ip_formated = ip_obj.ip_formated
        facade.delete_ipv4(ip_id)

    except Exception, exception:
        logger.exception(exception)
        raise api_exceptions.NetworkAPIException(exception)

    else:
        msg = {
            'object_type': 'Ipv4',
            'object_id': ip_id,
            'message': 'Ipv4 {} was deallocated with success.'.format(
                ip_formated)
        }
        return msg
