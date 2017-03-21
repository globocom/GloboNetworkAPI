# -*- coding: utf-8 -*-
from celery.exceptions import Ignore
from celery.utils.log import get_task_logger

from networkapi import celery_app
from networkapi.api_network.facade import v3 as facade
from networkapi.usuario.models import Usuario

logger = get_task_logger(__name__)


@celery_app.task(bind=True)
def create_networkv4(self, net_dict, user_id):

    msg = {
        'object_type': 'networkv4',
        'action': 'allocate',
    }
    self.update_state(
        state='PROGRESS',
        meta=msg
    )

    user = Usuario.objects.get(id=user_id)

    try:
        net = facade.create_networkipv4(net_dict, user)

    except Exception, exception:
        msg['message'] = 'NetworkV4 {} was not allocated.'.format(net)
        msg['reason'] = str(exception)
        self.update_state(
            state='FAILED',
            meta=msg
        )
        # ignore the task so no other state is recorded
        raise Ignore()

    else:
        msg['message'] = 'NetworkV4 {} was allocated with success.'.format(net)
        msg['object_id'] = net.id

        return msg


@celery_app.task(bind=True)
def update_networkv4(self, net_dict, user_id):

    msg = {
        'object_type': 'ipv4',
        'action': 'update',
        'object_id': net_dict.get('id')
    }
    self.update_state(
        state='PROGRESS',
        meta=msg
    )

    net_obj = facade.get_networkipv4_by_id(net_dict.get('id'))

    user = Usuario.objects.get(id=user_id)

    try:
        facade.update_networkipv4(net_dict, user)

    except Exception as exception:
        msg['message'] = 'NetworkV4 {} was not updated.'.format(net_obj)
        msg['reason'] = str(exception)
        update_networkv4.update_state(
            state='FAILED',
            meta=msg
        )

        # ignore the task so no other state is recorded
        raise Ignore()

    else:
        msg['message'] = 'NetworkV4 {} was updated with success.'.format(
            net_obj)

        return msg


@celery_app.task(bind=True)
def delete_networkv4(self, net_id):

    msg = {
        'object_type': 'networkv4',
        'action': 'deallocate',
        'object_id': net_id

    }
    self.update_state(
        state='PROGRESS',
        meta=msg
    )

    net_obj = facade.get_networkipv4_by_id(net_id)

    try:
        facade.delete_networkipv4(net_id)

    except Exception, exception:
        msg['message'] = 'NetworkV4 {} was not deallocated.'.format(net_obj)
        msg['reason'] = str(exception)
        self.update_state(
            state='FAILED',
            meta=msg
        )

        # ignore the task so no other state is recorded
        raise Ignore()

    else:
        msg['message'] = 'NetworkV4 {} was deallocated with success.'.\
            format(net_obj)

        return msg


@celery_app.task(bind=True)
def deploy_networkv4(self, net_id, user_id):

    msg = {
        'object_type': 'networkv4',
        'action': 'deploy',
        'object_id': net_id

    }
    self.update_state(
        state='PROGRESS',
        meta=msg
    )

    user = Usuario.objects.get(id=user_id)

    net_obj = facade.get_networkipv4_by_id(net_id)

    try:
        networkv4 = net_obj.networkv4
        status_deploy = facade.deploy_networkipv4(net_id, user)

    except Exception, exception:
        msg['message'] = 'NetworkV4 {} was not deployed.'.format(net_obj)
        msg['reason'] = str(exception)
        self.update_state(
            state='FAILED',
            meta=msg
        )

        # ignore the task so no other state is recorded
        raise Ignore()

    else:
        msg['message'] = 'NetworkV4 {} was deployed with success. {}'.format(
            networkv4, status_deploy)

        return msg


@celery_app.task(bind=True)
def undeploy_networkv4(self, net_id, user_id):

    msg = {
        'object_type': 'networkv4',
        'action': 'undeploy',
        'object_id': net_id

    }
    self.update_state(
        state='PROGRESS',
        meta=msg
    )

    user = Usuario.objects.get(id=user_id)

    net_obj = facade.get_networkipv4_by_id(net_id)

    try:
        networkv4 = net_obj.networkv4
        status_deploy = facade.undeploy_networkipv4(net_id, user)

    except Exception, exception:
        msg['message'] = 'NetworkV4 {} was not deployed.'.format(net_obj)
        msg['reason'] = str(exception)
        self.update_state(
            state='FAILED',
            meta=msg
        )

        # ignore the task so no other state is recorded
        raise Ignore()

    else:
        msg['message'] = 'NetworkV4 {} was undeployed with success. {}'.\
            format(networkv4, status_deploy)

        return msg
