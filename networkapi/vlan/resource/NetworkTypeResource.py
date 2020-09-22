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
from __future__ import with_statement

import logging

from networkapi.admin_permission import AdminPermission
from networkapi.auth import has_perm
from networkapi.distributedlock import distributedlock
from networkapi.distributedlock import LOCK_TYPE_NETWORK
from networkapi.exception import InvalidValueError
from networkapi.grupo.models import GrupoError
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.infrastructure.xml_utils import loads
from networkapi.infrastructure.xml_utils import XMLError
from networkapi.rest import RestResource
from networkapi.util import is_valid_int_greater_zero_param
from networkapi.util import is_valid_string_maxsize
from networkapi.util import is_valid_string_minsize
from networkapi.util import is_valid_vlan_name
from networkapi.vlan.models import NetTypeUsedByNetworkError
from networkapi.vlan.models import NetworkTypeNameDuplicatedError
from networkapi.vlan.models import NetworkTypeNotFoundError
from networkapi.vlan.models import TipoRede
from networkapi.vlan.models import VlanError


class NetworkTypeResource(RestResource):

    """Class to treat GET, POST, PUT and DELETE requests to table tipo_rede."""

    log = logging.getLogger('NetworkTypeResource')

    def handle_get(self, request, user, *args, **kwargs):
        """Treat GET requests to get all network types.

        URL: /net_type/
        """

        try:
            if not has_perm(user, AdminPermission.NETWORK_TYPE_MANAGEMENT, AdminPermission.READ_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                return self.not_authorized()

            results = TipoRede.objects.all()

            if results.count() > 0:
                map_list = []
                for item in results:
                    item_map = self.get_net_type_map(item)
                    map_list.append(item_map)

                # Build response (XML)
                return self.response(dumps_networkapi({'net_type': map_list}))
            else:
                # Build response (XML) to empty return
                return self.response(dumps_networkapi({}))

        except (VlanError, GrupoError):
            return self.response_error(1)

    def handle_post(self, request, user, *args, **kwargs):
        """Treat POST requests to add new network types.

        URL: /net_type/

        """

        try:
            # Check permission
            if not has_perm(user, AdminPermission.NETWORK_TYPE_MANAGEMENT, AdminPermission.WRITE_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                return self.not_authorized()

            # Get request XML data
            xml_map, attrs_map = loads(request.raw_post_data)

            # Get networkapi tag map
            networkapi_map = xml_map.get('networkapi')
            if networkapi_map is None:
                return self.response_error(3, u'There is no networkapi tag from request XML.')

            # Get net_type tag map
            net_type_map = networkapi_map.get('net_type')
            if net_type_map is None:
                return self.response_error(3, u'There is no tipo_rede tag from request XML.')

            # Valid name attribute
            name = net_type_map.get('name')
            if not is_valid_string_minsize(name, 3) or not is_valid_string_maxsize(name, 100):
                self.log.error(
                    u'Parameter %s is invalid. Value: %s.', 'name', name)
                raise InvalidValueError(None, 'name', name)

            if not is_valid_vlan_name(name):
                self.log.error(
                    u'Parameter %s is invalid because is using special characters and/or breaklines.', name)
                raise InvalidValueError(None, 'name', name)

            net_type = TipoRede(tipo_rede=name)

            if not is_valid_vlan_name(name):
                self.log.error(
                    u'Parameter %s is invalid because is using special characters and/or breaklines.', name)
                raise InvalidValueError(None, 'name', name)

            try:
                TipoRede.get_by_name(net_type.tipo_rede)
                raise NetworkTypeNameDuplicatedError(
                    None, u'Network type with name %s already exist' % net_type.tipo_rede)
            except NetworkTypeNotFoundError:
                pass

            try:
                net_type.save()
            except Exception, e:
                self.log.error(u'Failed to insert network type.')
                raise VlanError(e, u'Failed to insert network type.')

            net_type_map = dict()
            net_type_map['id'] = net_type.id

            return self.response(dumps_networkapi({'net_type': net_type_map}))

        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)
        except NetworkTypeNameDuplicatedError:
            return self.response_error(253, name)
        except XMLError, x:
            self.log.error(u'Error reading request XML.')
            return self.response_error(3, x)
        except (GrupoError, VlanError):
            return self.response_error(1)

    def handle_put(self, request, user, *args, **kwargs):
        """Treat PUT requests to edit network types.

        URL: /net_type/<id_net_type>/

        """

        try:
            # Check permission
            if not has_perm(user, AdminPermission.NETWORK_TYPE_MANAGEMENT, AdminPermission.WRITE_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                return self.not_authorized()

            # Get URL args
            id_net_type = kwargs.get('id_net_type')

            if not is_valid_int_greater_zero_param(id_net_type):
                self.log.error(
                    u'Parameter %s is invalid. Value: %s.', 'id_net_type', id_net_type)
                raise InvalidValueError(None, 'id_net_type', id_net_type)

            # Get XML data
            xml_map, attrs_map = loads(request.raw_post_data)

            # Get networkapi tag map
            networkapi_map = xml_map.get('networkapi')
            if networkapi_map is None:
                return self.response_error(3, u'There is no networkapi tag from request XML.')

            # Get net_type tag map
            net_type_map = networkapi_map.get('net_type')
            if net_type_map is None:
                return self.response_error(3, u'There is no net_type tag from request XML.')

            # Valid name attribute
            name = net_type_map.get('name')
            if not is_valid_string_minsize(name, 3) or not is_valid_string_maxsize(name, 100):
                self.log.error(
                    u'Parameter %s is invalid. Value: %s.', 'name', name)
                raise InvalidValueError(None, 'name', name)

            net_type = TipoRede.get_by_pk(id_net_type)

            with distributedlock(LOCK_TYPE_NETWORK % id_net_type):

                try:
                    if name.lower() != net_type.tipo_rede.lower():
                        TipoRede.get_by_name(name)
                        raise NetworkTypeNameDuplicatedError(
                            None, u'Network type with name %s already exists' % name)
                except NetworkTypeNotFoundError:
                    pass

                net_type.tipo_rede = name
                try:
                    net_type.save()
                except Exception, e:
                    self.log.error(u'Failed to edit network type.')
                    raise VlanError(e, u'Failed to edit network type.')

            # Return empty response
            return self.response(dumps_networkapi({}))

        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)
        except XMLError, x:
            self.log.error(u'Erro ao ler o XML da requisição.')
            return self.response_error(3, x)
        except NetworkTypeNotFoundError:
            return self.response_error(111)
        except NetworkTypeNameDuplicatedError:
            return self.response_error(253, name)
        except (GrupoError, VlanError):
            return self.response_error(1)

    def handle_delete(self, request, user, *args, **kwargs):
        """Treat DELETE request to remove network type

        URL: /net_type/<id_net_type>/

        """

        try:
            # Check permission
            if not has_perm(user, AdminPermission.NETWORK_TYPE_MANAGEMENT, AdminPermission.WRITE_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                return self.not_authorized()

            # Get URL args
            id_net_type = kwargs.get('id_net_type')

            if not is_valid_int_greater_zero_param(id_net_type):
                self.log.error(
                    u'Parameter %s is invalid. Value: %s.', 'id_net_type', id_net_type)
                raise InvalidValueError(None, 'id_net_type', id_net_type)

            net_type = TipoRede.get_by_pk(id_net_type)

            with distributedlock(LOCK_TYPE_NETWORK % id_net_type):

                # Check if network type is used by vlan
                if net_type.networkipv4_set.count() > 0 or net_type.networkipv6_set.count() > 0:
                    self.log.error(u'Network type used by network.')
                    raise NetTypeUsedByNetworkError(
                        None, u'Network type used by network.')

                try:
                    net_type.delete()
                except Exception, e:
                    self.log.error(u'Failed to remove network type.')
                    raise VlanError(e, u'Failed to remove network type.')

            # Return empty response
            return self.response(dumps_networkapi({}))

        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)
        except NetworkTypeNotFoundError:
            return self.response_error(111)
        except NetTypeUsedByNetworkError:
            return self.response_error(215, id_net_type)
        except (GrupoError, VlanError):
            return self.response_error(1)

    def get_net_type_map(self, tipo_rede):
        map = dict()
        map['id'] = tipo_rede.id
        map['name'] = tipo_rede.tipo_rede
        return map
