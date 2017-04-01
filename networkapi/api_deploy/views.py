# -*- coding: utf-8 -*-
# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import logging
import time

from rest_framework.decorators import api_view
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from networkapi.api_deploy import exceptions
from networkapi.api_deploy import facade
from networkapi.api_deploy.permissions import DeployConfig
from networkapi.api_rest import exceptions as api_exceptions
from networkapi.distributedlock import LOCK_EQUIPMENT_DEPLOY_CONFIG_USERSCRIPT
from networkapi.queue_tools import queue_keys
from networkapi.queue_tools.rabbitmq import QueueManager
from networkapi.settings import USER_SCRIPTS_REL_PATH

log = logging.getLogger(__name__)


@api_view(['PUT'])
@permission_classes((IsAuthenticated, DeployConfig))
def deploy_sync_copy_script_to_equipment(request, equipment_id):
    """
    Deploy configuration on equipment(s)
    Default source: TFTP SERVER
    Default destination: apply config (running-config)
    Default protocol: tftp
    Receives script
    """

    try:
        script = request.DATA['script_data']
        request_identifier = request.DATA['identifier']
        script_file = facade.create_file_from_script(
            script, USER_SCRIPTS_REL_PATH)
        equipment_id = int(equipment_id)
        lockvar = LOCK_EQUIPMENT_DEPLOY_CONFIG_USERSCRIPT % (equipment_id)
        data = dict()
        if request_identifier is not None:
            queue_manager = QueueManager(broker_vhost='tasks',
                                         queue_name='tasks.aclapi',
                                         exchange_name='tasks.aclapi',
                                         routing_key='tasks.aclapi')
            data = {'timestamp': int(time.time())}
            queue_manager.append({
                'action': queue_keys.BEGIN_DEPLOY_SYNC_SCRIPT,
                'identifier': request_identifier,
                'data': data})
            queue_manager.send()
        data['output'] = facade.deploy_config_in_equipment_synchronous(
            script_file, equipment_id, lockvar)
        data['status'] = 'OK'
        if request_identifier is not None:
            queue_manager = QueueManager(broker_vhost='tasks',
                                         queue_name='tasks.aclapi',
                                         exchange_name='tasks.aclapi',
                                         routing_key='tasks.aclapi')
            data = {'timestamp': int(time.time()), 'status': 'OK'}
            queue_manager.append({'action': queue_keys.END_DEPLOY_SYNC_SCRIPT,
                                  'identifier': request_identifier, 'data': data})
            queue_manager.send()
        return Response(data)

    except KeyError, key:
        log.error(key)
        raise exceptions.InvalidKeyException(key)


@api_view(['PUT'])
@permission_classes((IsAuthenticated, DeployConfig))
def deploy_sync_copy_script_to_multiple_equipments(request):
    """
    Deploy configuration on equipment(s)
    Default source: TFTP SERVER
    Default destination: apply config (running-config)
    Default protocol: tftp
    Receives script
    """

    try:
        script = request.DATA['script_data']
        id_equips = request.DATA['id_equips']

        # Check equipment permissions
        for id_equip in id_equips:
            # TODO
            pass

        output_data = dict()

        script_file = facade.create_file_from_script(
            script, USER_SCRIPTS_REL_PATH)
        for id_equip in id_equips:
            equipment_id = int(id_equip)
            lockvar = LOCK_EQUIPMENT_DEPLOY_CONFIG_USERSCRIPT % (equipment_id)
            output_data[equipment_id] = dict()
            try:
                output_data[equipment_id]['output'] = facade.deploy_config_in_equipment_synchronous(
                    script_file, equipment_id, lockvar)
                output_data[equipment_id]['status'] = 'OK'
            except Exception, e:
                log.error('Error applying script file to equipment_id %s: %s' % (
                    equipment_id, e))
                output_data[equipment_id]['output'] = str(e)
                output_data[equipment_id]['status'] = 'ERROR'

        return Response(output_data)
    except KeyError, key:
        log.error(key)
        raise exceptions.InvalidKeyException(key)
    except Exception, exception:
        log.error(exception)
        raise api_exceptions.NetworkAPIException()
