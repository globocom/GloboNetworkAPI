# -*- coding: utf-8 -*-
from celery.utils.log import get_task_logger

from networkapi import celery_app
from networkapi.api_ip import facade
from networkapi.api_task.classes import BaseTask
from networkapi.usuario.models import Usuario


logger = get_task_logger(__name__)


@celery_app.task(bind=True, base=BaseTask)
def create_ipv6(self, ip_dict, user_id):

    msg = {
        'object_type': 'ipv6',
        'action': 'allocate',
    }
    self.update_state(
        state='PROGRESS',
        meta=msg
    )

    user = Usuario.objects.get(id=user_id)

    try:
        ip = facade.create_ipv6(ip_dict, user)

    except Exception, exception:
        msg['message'] = 'IPv6 {} was not allocated.'.format(ip)
        msg['reason'] = str(exception)

        raise Exception(msg)

    else:
        msg['message'] = 'IPv6 {} was allocated with success.'.format(ip)
        msg['object_id'] = ip.id

        return msg


@celery_app.task(bind=True, base=BaseTask)
def update_ipv6(self, ip_dict, user_id):

    msg = {
        'object_type': 'ipv6',
        'action': 'update',
        'object_id': ip_dict.get('id')
    }
    self.update_state(
        state='PROGRESS',
        meta=msg
    )

    ip_obj = facade.get_ipv6_by_id(ip_dict.get('id'))

    user = Usuario.objects.get(id=user_id)

    try:
        facade.update_ipv6(ip_dict, user)

    except Exception, exception:
        msg['message'] = 'IPv6 {} was not updated.'.format(ip_obj)
        msg['reason'] = str(exception)

        raise Exception(msg)

    else:
        msg['message'] = 'IPv6 {} was updated with success.'.format(ip_obj)

        return msg


@celery_app.task(bind=True, base=BaseTask)
def delete_ipv6(self, ip_id, user_id):

    msg = {
        'object_type': 'ipv6',
        'action': 'deallocate',
        'object_id': ip_id
    }
    self.update_state(
        state='PROGRESS',
        meta=msg
    )

    ip_obj = facade.get_ipv6_by_id(ip_id)

    try:
        facade.delete_ipv6(ip_id)

    except Exception, exception:
        msg['message'] = 'IPv6 {} was not deallocated.'.format(ip_obj)
        msg['reason'] = str(exception)

        raise Exception(msg)

    else:
        msg['message'] = 'IPv6 {} was deallocated with success.'.format(ip_obj)

        return msg
