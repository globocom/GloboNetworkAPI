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

from django.forms.models import model_to_dict

from networkapi.acl.acl import checkAclCvs
from networkapi.acl.acl import createAclCvs
from networkapi.acl.Enum import NETWORK_TYPES
from networkapi.admin_permission import AdminPermission
from networkapi.ambiente.models import IP_VERSION
from networkapi.auth import has_perm
from networkapi.exception import InvalidValueError
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.infrastructure.xml_utils import loads
from networkapi.infrastructure.xml_utils import XMLError
from networkapi.queue_tools import queue_keys
from networkapi.queue_tools.rabbitmq import QueueManager
from networkapi.rest import RestResource
from networkapi.util import get_environment_map
from networkapi.util import is_valid_int_greater_zero_param
from networkapi.util import is_valid_version_ip
from networkapi.vlan.models import Vlan
from networkapi.vlan.models import VlanACLDuplicatedError
from networkapi.vlan.models import VlanNotFoundError
from networkapi.vlan.serializers import VlanSerializer


class VlanCreateAclResource(RestResource):

    log = logging.getLogger('VlanCreateAcl')

    CODE_MESSAGE_FAIL_READ_XML = 3
    CODE_MESSAGE_VLAN_NOT_FOUND = 116
    CODE_MESSAGE_INVALID_PARAM = 269
    CODE_MESSAGE_DUPLICATE_ACL = 367
    CODE_MESSAGE_ACL_NOT_CREATED = 364

    def handle_post(self, request, user, *args, **kwargs):
        """Treat POST requests to Create ACL

        URL: vlan/create/acl/
        """
        self.log.info('Create ACL Vlan')

        try:
            is_suggest_acl_name = False
            # User permission
            if not has_perm(user, AdminPermission.VLAN_MANAGEMENT, AdminPermission.WRITE_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                return self.not_authorized()

            # Load XML data
            xml_map, _ = loads(
                request.raw_post_data, ['searchable_columns', 'asorting_cols'])

            # XML data format
            networkapi_map = xml_map.get('networkapi')
            self.validate_networkapi_map(networkapi_map)

            vlan_map = networkapi_map.get('vlan')
            self.validate_vlan_map(vlan_map)

            id_vlan = vlan_map.get('id_vlan')
            network_type = vlan_map.get('network_type')

            self.validate_id_vlan(id_vlan)

            self.validate_ip_version(network_type)

            vlan = Vlan().get_by_pk(id_vlan)

            environment = get_environment_map(vlan.ambiente)

            if network_type == NETWORK_TYPES.v4:
                if not vlan.acl_file_name:
                    is_suggest_acl_name = True
                    vlan.acl_file_name = self.__create_suggest_acl_name(vlan)

                acl_name = vlan.acl_file_name
            else:
                if not vlan.acl_file_name_v6:
                    is_suggest_acl_name = True
                    vlan.acl_file_name_v6 = self.__create_suggest_acl_name(
                        vlan)

                acl_name = vlan.acl_file_name_v6

            self.validate_duplicate_acl(
                acl_name, environment, network_type, user)

            if is_suggest_acl_name:
                vlan.save()

            createAclCvs(acl_name, environment, network_type, user)

            # Send to Queue
            queue_manager = QueueManager(broker_vhost='tasks',
                                         queue_name='tasks.aclapi',
                                         exchange_name='tasks.aclapi',
                                         routing_key='tasks.aclapi')

            serializer = VlanSerializer(vlan)
            data_to_queue = serializer.data
            data_to_queue.update({'description': queue_keys.VLAN_CREATE_ACL})
            queue_manager.append({'action': queue_keys.VLAN_CREATE_ACL,
                                  'kind': queue_keys.VLAN_KEY, 'data': data_to_queue})

            queue_manager.send()

            return self.response(dumps_networkapi({'vlan': model_to_dict(vlan)}))

        except InvalidValueError, e:
            return self.response_error(self.CODE_MESSAGE_INVALID_PARAM, e.param, e.value)

        except VlanACLDuplicatedError, e:
            return self.response_error(self.CODE_MESSAGE_DUPLICATE_ACL, acl_name)

        except VlanNotFoundError, e:
            self.log.error(e.message)
            return self.response_error(self.CODE_MESSAGE_VLAN_NOT_FOUND)

        except XMLError, e:
            return self.response_error(self.CODE_MESSAGE_FAIL_READ_XML)

    def __create_suggest_acl_name(self, vlan_object):
        return str(vlan_object.nome + vlan_object.ambiente.ambiente_logico.nome).replace(' ', '')

    def validate_duplicate_acl(self, acl_name, environment, network_type, user):
        if checkAclCvs(acl_name, environment, network_type, user):
            self.log.error(
                u'There is already an Vlan with the Acl - Ipv4 = %s.' % acl_name)
            raise VlanACLDuplicatedError('Duplicate ACL')

    def validate_networkapi_map(self, networkapi_map):
        if networkapi_map is None:
            self.log.error(
                u'There is no value to the networkapi tag of XML request.')
            raise XMLError(None, None)

    def validate_vlan_map(self, vlan_map):
        if vlan_map is None:
            self.log.error(
                u'There is no value to the vlan tag of XML request.')
            raise XMLError(None, None)

    def validate_id_vlan(self, id_vlan):
        if not is_valid_int_greater_zero_param(id_vlan):
            self.log.error(
                u'The id_valan parameter is not a valid value: %s.', id_vlan)
            raise InvalidValueError('Invalid Id For Vlan', 'id_vlan', id_vlan)

    def validate_ip_version(self, network_type):
        if not is_valid_version_ip(network_type, IP_VERSION):
            self.log.error(
                u'The type network parameter is invalid value: %s.', network_type)
            raise InvalidValueError(
                'Invalid Network Type', 'network_type', network_type)
