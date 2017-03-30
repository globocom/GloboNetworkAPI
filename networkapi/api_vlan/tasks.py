# -*- coding: utf-8 -*-
from celery.utils.log import get_task_logger

from networkapi import celery_app
from networkapi.api_task.classes import BaseTask
from networkapi.api_vlan.facade import v3 as facade
from networkapi.usuario.models import Usuario


logger = get_task_logger(__name__)


@celery_app.task(bind=True, base=BaseTask)
def create_vlan(self, vlan_dict, user_id):

    msg = {
        'object_type': 'vlan',
        'action': 'allocate'
    }
    self.update_state(
        state='PROGRESS',
        meta=msg
    )

    user = Usuario.objects.get(id=user_id)

    try:
        vlan_obj = facade.create_vlan(vlan_dict, user)

    except Exception, exception:
        msg['message'] = 'Vlan was not allocated.'
        msg['reason'] = str(exception)

        raise Exception(msg)

    else:
        msg['message'] = 'Vlan {} was allocated with success.'.format(vlan_obj)

        return msg


@celery_app.task(bind=True, base=BaseTask)
def update_vlan(self, vlan_dict, user_id):

    vlan_id = vlan_dict.get('id')
    msg = {
        'object_type': 'vlan',
        'action': 'update',
        'object_id': vlan_id
    }
    self.update_state(
        state='PROGRESS',
        meta=msg
    )

    vlan_obj = facade.get_vlan_by_id(vlan_id)

    user = Usuario.objects.get(id=user_id)

    try:
        facade.update_vlan(vlan_dict, user)

    except Exception, exception:
        msg['message'] = 'Vlan was not updated.'.format(vlan_obj)
        msg['reason'] = str(exception)

        raise Exception(msg)

    else:
        msg['message'] = 'Vlan {} was updated with success.'.format(vlan_obj)

        return msg


@celery_app.task(bind=True, base=BaseTask)
def delete_vlan(self, vlan_id, user_id):

    msg = {
        'object_type': 'vlan',
        'action': 'deallocate',
        'object_id': vlan_id
    }
    self.update_state(
        state='PROGRESS',
        meta=msg
    )

    vlan_obj = facade.get_vlan_by_id(vlan_id)

    try:
        facade.delete_vlan(vlan_id)

    except Exception, exception:
        msg['message'] = 'Vlan was not deallocated.'.format(vlan_obj)
        msg['reason'] = str(exception)

        raise Exception(msg)

    else:
        msg['message'] = 'Vlan {} was deallocated with success.'.format(
            vlan_obj)

        return msg
