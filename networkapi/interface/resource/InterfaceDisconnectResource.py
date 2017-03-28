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
from networkapi.api_interface import exceptions as api_interface_exceptions
from networkapi.auth import has_perm
from networkapi.distributedlock import distributedlock
from networkapi.distributedlock import LOCK_INTERFACE
from networkapi.equipamento.models import EquipamentoError
from networkapi.exception import InvalidValueError
from networkapi.grupo.models import GrupoError
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.infrastructure.xml_utils import XMLError
from networkapi.interface.models import Interface
from networkapi.interface.models import InterfaceError
from networkapi.interface.models import InterfaceInvalidBackFrontError
from networkapi.interface.models import InterfaceNotFoundError
from networkapi.interface.models import PortChannel
from networkapi.rest import RestResource
from networkapi.util import is_valid_int_greater_zero_param
from networkapi.util import is_valid_zero_one_param


class InterfaceDisconnectResource(RestResource):

    log = logging.getLogger('InterfaceDisconnectResource')

    def handle_delete(self, request, user, *args, **kwargs):
        """Treat DELETE requests to remove the connection of two interfaces by front or back

        URL: interface/<id_interface>/<back_or_front>/
        """

        try:

            self.log.info('Disconnect')

            # Valid Interface ID
            id_interface = kwargs.get('id_interface')
            if not is_valid_int_greater_zero_param(id_interface):
                self.log.error(
                    u'The id_interface parameter is not a valid value: %s.', id_interface)
                raise InvalidValueError(None, 'id_interface', id_interface)

            # Valid back or front param
            back_or_front = kwargs.get('back_or_front')
            if not is_valid_zero_one_param(back_or_front):
                self.log.error(
                    u'The back_or_front parameter is not a valid value: %s.', back_or_front)
                raise InvalidValueError(None, 'back_or_front', back_or_front)
            else:
                back_or_front = int(back_or_front)

            # User permission equip 1
            if not has_perm(user, AdminPermission.EQUIPMENT_MANAGEMENT, AdminPermission.WRITE_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                return self.not_authorized()

            # Checks if interface exists in database
            interface_1 = Interface.get_by_pk(id_interface)

            with distributedlock(LOCK_INTERFACE % id_interface):

                if interface_1.channel:
                    raise api_interface_exceptions.InterfaceException(
                        'Interface está em um Port Channel')

                # Is valid back or front connection
                if back_or_front:
                    try:
                        interface_2 = Interface.get_by_pk(
                            interface_1.ligacao_front_id)
                    except InterfaceNotFoundError:
                        raise InterfaceInvalidBackFrontError(
                            None, 'Interface two has no connection with front of Interface one')
                else:
                    try:
                        interface_2 = Interface.get_by_pk(
                            interface_1.ligacao_back_id)
                    except InterfaceNotFoundError:
                        raise InterfaceInvalidBackFrontError(
                            None, 'Interface two has no connection with back of Interface one')

                if interface_2.channel:
                    raise api_interface_exceptions.InterfaceException(
                        'Interface está em um Port Channel')

                if interface_2.ligacao_front_id == interface_1.id:
                    back_or_front_2 = 1
                elif interface_2.ligacao_back_id == interface_1.id:
                    back_or_front_2 = 0
                else:
                    raise InterfaceInvalidBackFrontError(
                        None, 'Interface one has no connection with front or back of Interface two')

                # Business Rules

                # Remove Interface one connection
                if back_or_front:
                    interface_1.ligacao_front = None
                else:
                    interface_1.ligacao_back = None

                # Remove Interface two connection
                if back_or_front_2:
                    interface_2.ligacao_front = None
                else:
                    interface_2.ligacao_back = None

                # Save
                interface_1.save()
                interface_2.save()

            # Return None for success
            return self.response(dumps_networkapi({}))

        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)
        except InterfaceInvalidBackFrontError, e:
            return self.response_error(307, e.message)
        except InterfaceNotFoundError:
            return self.response_error(141)
        except (InterfaceError, GrupoError, EquipamentoError):
            return self.response_error(1)
        except api_interface_exceptions.InterfaceException:
            return self.response_error(413)
        except XMLError, e:
            self.log.error(u'Error reading the XML request.')
            return self.response_error(3, e)
