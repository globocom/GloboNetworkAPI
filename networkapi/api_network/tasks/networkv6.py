# -*- coding: utf-8 -*-
from celery.utils.log import get_task_logger

from networkapi import celery_app
from networkapi.api_network.facade import v3 as facade
from networkapi.api_task.classes import BaseTask
from networkapi.usuario.models import Usuario


logger = get_task_logger(__name__)


@celery_app.task(bind=True, base=BaseTask)
def create_networkv6(self, net_dict, user_id):

    msg = {
        'object_type': 'networkv6',
        'action': 'allocate',
    }
    self.update_state(
        state='PROGRESS',
        meta=msg
    )

    user = Usuario.objects.get(id=user_id)

    try:
        net = facade.create_networkipv6(net_dict, user)

    except Exception, exception:
        msg['message'] = 'NetworkV6 was not allocated.'
        msg['reason'] = str(exception)

        raise Exception(msg)

    else:
        msg['message'] = 'NetworkV6 {} was allocated with success.'.format(net)
        msg['object_id'] = net.id

        return msg


@celery_app.task(bind=True, base=BaseTask)
def update_networkv6(self, net_dict, user_id):

    msg = {
        'object_type': 'ipv6',
        'action': 'update',
        'object_id': net_dict.get('id')
    }
    self.update_state(
        state='PROGRESS',
        meta=msg
    )

    net_obj = facade.get_networkipv6_by_id(net_dict.get('id'))

    user = Usuario.objects.get(id=user_id)

    try:
        net = facade.update_networkipv6(net_dict, user)

    except Exception, exception:
        msg['message'] = 'NetworkV6 {} was not updated.'.format(net_obj)
        msg['reason'] = str(exception)

        raise Exception(msg)

    else:
        msg['message'] = 'NetworkV6 {} was updated with success.'.format(
            net_obj)
        msg['object_id'] = net.id

        return msg


@celery_app.task(bind=True, base=BaseTask)
def delete_networkv6(self, net_id, user_id):

    msg = {
        'object_type': 'networkv6',
        'action': 'deallocate',
        'object_id': net_id

    }
    self.update_state(
        state='PROGRESS',
        meta=msg
    )

    net_obj = facade.get_networkipv6_by_id(net_id)

    try:
        facade.delete_networkipv6(net_id)

    except Exception, exception:
        msg['message'] = 'NetworkV6 {} was not deallocated.'.format(net_obj)
        msg['reason'] = str(exception)

        raise Exception(msg)

    else:
        msg['message'] = 'NetworkV6 {} was deallocated with success.'.\
            format(net_obj)

        return msg


@celery_app.task(bind=True, base=BaseTask)
def deploy_networkv6(self, net_id, user_id):

    msg = {
        'object_type': 'networkv6',
        'action': 'deploy',
        'object_id': net_id

    }
    self.update_state(
        state='PROGRESS',
        meta=msg
    )

    user = Usuario.objects.get(id=user_id)

    net_obj = facade.get_networkipv6_by_id(net_id)

    try:
        networkv6 = net_obj.networkv6
        status_deploy = facade.deploy_networkipv6(net_id, user)

    except Exception, exception:
        msg['message'] = 'NetworkV6 {} was not deployed.'.format(net_obj)
        msg['reason'] = str(exception)

        raise Exception(msg)

    else:
        msg['message'] = 'NetworkV6 {} was deployed with success. {}'.format(
            networkv6, status_deploy)

        return msg


@celery_app.task(bind=True, base=BaseTask)
def undeploy_networkv6(self, net_id, user_id):

    msg = {
        'object_type': 'networkv6',
        'action': 'undeploy',
        'object_id': net_id

    }
    self.update_state(
        state='PROGRESS',
        meta=msg
    )

    user = Usuario.objects.get(id=user_id)

    net_obj = facade.get_networkipv6_by_id(net_id)

    try:
        networkv6 = net_obj.networkv6
        status_deploy = facade.undeploy_networkipv6(net_id, user)

    except Exception, exception:
        msg['message'] = 'NetworkV6 {} was not deployed.'.format(net_obj)
        msg['reason'] = str(exception)

        raise Exception(msg)

    else:
        msg['message'] = 'NetworkV6 {} was undeployed with success. {}'.\
            format(networkv6, status_deploy)

        return msg
