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

from django.db import transaction
from django.db.utils import IntegrityError

from networkapi.admin_permission import AdminPermission
from networkapi.ambiente.models import EnvironmentVip
from networkapi.ambiente.models import IP_VERSION
from networkapi.auth import has_perm
from networkapi.distributedlock import distributedlock
from networkapi.distributedlock import LOCK_VIP_IP_EQUIP
from networkapi.equipamento.models import EquipamentoError
from networkapi.equipamento.models import EquipamentoNotFoundError
from networkapi.exception import InvalidValueError
from networkapi.grupo.models import EGrupoNotFoundError
from networkapi.grupo.models import GrupoError
from networkapi.infrastructure.script_utils import exec_script
from networkapi.infrastructure.script_utils import ScriptError
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.infrastructure.xml_utils import loads
from networkapi.ip.models import IpEquipamento
from networkapi.ip.models import IpEquipmentNotFoundError
from networkapi.ip.models import IpError
from networkapi.ip.models import IpNotFoundByEquipAndVipError
from networkapi.ip.models import IpNotFoundError
from networkapi.ip.models import Ipv6Equipament
from networkapi.requisicaovips.models import RequestVipWithoutServerPoolError
from networkapi.requisicaovips.models import RequisicaoVips
from networkapi.requisicaovips.models import RequisicaoVipsError
from networkapi.requisicaovips.models import RequisicaoVipsNotFoundError
from networkapi.requisicaovips.models import ServerPoolMember
from networkapi.rest import RestResource
from networkapi.rest import UserNotAuthorizedError
from networkapi.settings import VIP_REAL_v4_CHECK
from networkapi.settings import VIP_REAL_v4_CREATE
from networkapi.settings import VIP_REAL_v4_DISABLE
from networkapi.settings import VIP_REAL_v4_ENABLE
from networkapi.settings import VIP_REAL_v4_REMOVE
from networkapi.settings import VIP_REAL_v6_CHECK
from networkapi.settings import VIP_REAL_v6_CREATE
from networkapi.settings import VIP_REAL_v6_DISABLE
from networkapi.settings import VIP_REAL_v6_ENABLE
from networkapi.settings import VIP_REAL_v6_REMOVE
from networkapi.settings import VIP_REALS_v4_CHECK
from networkapi.settings import VIP_REALS_v4_CREATE
from networkapi.settings import VIP_REALS_v4_DISABLE
from networkapi.settings import VIP_REALS_v4_ENABLE
from networkapi.settings import VIP_REALS_v4_REMOVE
from networkapi.settings import VIP_REALS_v6_CHECK
from networkapi.settings import VIP_REALS_v6_CREATE
from networkapi.settings import VIP_REALS_v6_DISABLE
from networkapi.settings import VIP_REALS_v6_ENABLE
from networkapi.settings import VIP_REALS_v6_REMOVE
from networkapi.util import is_valid_int_greater_zero_param
from networkapi.util.decorators import deprecated


class RequestVipsRealResource(RestResource):

    log = logging.getLogger('RequestVipsRealResource')

    @deprecated(new_uri='api/pool/check_status|save/')
    def handle_post(self, request, user, *args, **kwargs):
        """Treat requests POST to Add/Del/Enable/Disable/Check requestIP - Real.

        URLs: /vip/real/ or /real/equip/<id_equip>/vip/<id_vip>/ip/<id_ip>/
        """
        self.log.info('Add/Del/Ena/Dis/Chk request VIP - Real')

        try:
            parameter = request.path.split('/')[2]
            if parameter == 'equip':
                operation = 'add'
                # Get URL data
                vip_id = int(kwargs.get('id_vip'))
                equip_id = int(kwargs.get('id_equip'))
                ip_id = int(kwargs.get('id_ip'))
                network_version = IP_VERSION.IPv4[0]
            else:
                # Load XML data
                xml_map, attrs_map = loads(request.raw_post_data)

                # XML data format
                networkapi_map = xml_map.get('networkapi')
                if networkapi_map is None:
                    return self.response_error(3, u'There is no value to the networkapi tag of XML request.')

                vip_map = networkapi_map.get('vip')
                if vip_map is None:
                    return self.response_error(3, u'There is no value to the vip tag of XML request.')

                # Get XML data
                vip_id = vip_map.get('vip_id')
                equip_id = vip_map.get('equip_id')
                ip_id = vip_map.get('ip_id')
                operation = vip_map.get('operation')
                network_version = vip_map.get('network_version')

                port_vip = None
                port_real = None
                if 'port_vip' in vip_map and 'port_real' in vip_map:
                    port_vip = vip_map.get('port_vip')
                    port_real = vip_map.get('port_real')

            return self.administrate_real(user, vip_id, equip_id, ip_id, operation, network_version, port_vip, port_real)

        except UserNotAuthorizedError:
            return self.not_authorized()

        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)

        except ScriptError, e:
            return self.response_error(2, e)

        except IpNotFoundError:
            return self.response_error(119)

        except RequisicaoVipsNotFoundError:
            return self.response_error(152)

        except EquipamentoNotFoundError:
            return self.response_error(117, equip_id)

        except EGrupoNotFoundError:
            return self.response_error(102)

        except IpEquipmentNotFoundError:
            return self.response_error(118, ip_id, equip_id)

        except IpNotFoundByEquipAndVipError, e:
            return self.response_error(334, e.message)

        except RequestVipWithoutServerPoolError, e:
            return self.response_error(374, e.message)

        except (RequisicaoVipsError, EquipamentoError, IpError, GrupoError):
            return self.response_error(1)

        except Exception, e:
            if isinstance(e, IntegrityError):
                # Duplicate value for Port Vip, Port Real and IP
                return self.response_error(353)
            else:
                return self.response_error(1)

    @deprecated(new_uri='api/pool/check_status|save/')
    def handle_put(self, request, user, *args, **kwargs):
        """Treat requests PUT to Enable/Disable/ request VIP - Real.
        URLs: /real/<status>/equip/<id_equip>/vip/<id_vip>/ip/<id_ip>)/
        """
        self.log.info('Ena/Dis/ request VIP - Real')

        try:
            parameter = request.path.split('/')[2]

            if parameter == 'enable':
                operation = 'ena'
            elif parameter == 'check':
                operation = 'chk'
            else:
                operation = 'dis'

            # Get URL data
            vip_id = int(kwargs.get('id_vip'))
            equip_id = int(kwargs.get('id_equip'))
            ip_id = int(kwargs.get('id_ip'))
            network_version = IP_VERSION.IPv4[0]

            return self.administrate_real(user, vip_id, equip_id, ip_id, operation, network_version)

        except UserNotAuthorizedError:
            return self.not_authorized()

        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)

        except ScriptError, e:
            return self.response_error(2, e)

        except IpNotFoundError:
            return self.response_error(119)

        except RequisicaoVipsNotFoundError:
            return self.response_error(152)

        except EquipamentoNotFoundError:
            return self.response_error(117, equip_id)

        except EGrupoNotFoundError:
            return self.response_error(102)

        except IpEquipmentNotFoundError:
            return self.response_error(118, ip_id, equip_id)

        except (RequisicaoVipsError, EquipamentoError, IpError, GrupoError):
            return self.response_error(1)

    @deprecated(new_uri='api/pool/check_status|save/')
    def handle_delete(self, request, user, *args, **kwargs):
        """Treat requests POST to Del request VIP - Real.

        URLs: /real/equip/<id_equip>/vip/<id_vip>/ip/<id_ip>/
        """
        self.log.info('Del request VIP - Real')

        try:
            parameter = request.path.split('/')[2]

            if parameter == 'equip':
                operation = 'del'
                # Get URL data
                vip_id = int(kwargs.get('id_vip'))
                equip_id = int(kwargs.get('id_equip'))
                ip_id = int(kwargs.get('id_ip'))
                network_version = IP_VERSION.IPv4[0]

            return self.administrate_real(user, vip_id, equip_id, ip_id, operation, network_version)

        except UserNotAuthorizedError:
            return self.not_authorized()

        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)

        except ScriptError, e:
            return self.response_error(2, e)

        except IpNotFoundError:
            return self.response_error(119)

        except RequisicaoVipsNotFoundError:
            return self.response_error(152)

        except EquipamentoNotFoundError:
            return self.response_error(117, equip_id)

        except EGrupoNotFoundError:
            return self.response_error(102)

        except IpEquipmentNotFoundError:
            return self.response_error(118, ip_id, equip_id)

        except (RequisicaoVipsError, EquipamentoError, IpError, GrupoError):
            return self.response_error(1)

    def administrate_real(self, user, vip_id, equip_id, ip_id, operation, network_version, port_vip=None, port_real=None):

        # Valid VIP ID
        if not is_valid_int_greater_zero_param(vip_id):
            self.log.error(
                u'The vip_id parameter is not a valid value: %s.', vip_id)
            raise InvalidValueError(None, 'vip_id', vip_id)

        # Valid Equipament ID
        if not is_valid_int_greater_zero_param(equip_id):
            self.log.error(
                u'The equip_id parameter is not a valid value: %s.', equip_id)
            raise InvalidValueError(None, 'equip_id', equip_id)

        # Valid IP ID
        if not is_valid_int_greater_zero_param(ip_id):
            self.log.error(
                u'The ip_id parameter is not a valid value: %s.', ip_id)
            raise InvalidValueError(None, 'ip_id', ip_id)

        # Valid operation
        if operation not in ['add', 'del', 'ena', 'dis', 'chk']:
            self.log.error(
                u'The operation parameter is not a valid value: %s.', operation)
            raise InvalidValueError(None, 'operation', operation)

        # Valid network version
        if network_version not in ['v4', 'v6']:
            self.log.error(
                u'The network_version parameter is not a valid value: %s.', network_version)
            raise InvalidValueError(None, 'network_version', network_version)

        # User permission
        if (operation == 'chk'):
            if not has_perm(user, AdminPermission.VIP_ALTER_SCRIPT, AdminPermission.READ_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                raise UserNotAuthorizedError(None)
        else:
            if not has_perm(user, AdminPermission.VIP_ALTER_SCRIPT, AdminPermission.WRITE_OPERATION, None, equip_id, AdminPermission.EQUIP_UPDATE_CONFIG_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                raise UserNotAuthorizedError(None)

        # new_call = True - New calls for Add/Del/Enable/Disable/Check with new params (Port Vip and Port Real)
        # new_call = False = Old calls for compatibility
        new_call = False
        if port_vip is not None and port_real is not None:
            # Valid ports
            if not is_valid_int_greater_zero_param(port_vip):
                self.log.error(
                    u'The port_vip parameter is not a valid value: %s.', port_vip)
                raise InvalidValueError(None, 'port_vip', port_vip)

            if not is_valid_int_greater_zero_param(port_real):
                self.log.error(
                    u'The port_vip parameter is not a valid value: %s.', port_real)
                raise InvalidValueError(None, 'port_real', port_real)

            new_call = True

        # Find Request VIP by ID to check if it exist
        vip = RequisicaoVips.get_by_pk(vip_id)
        # Get variables
        variables_map = vip.variables_to_map()
        # Valid variables
        # vip.set_variables(variables_map)

        evip = EnvironmentVip.get_by_values(variables_map.get(
            'finalidade'), variables_map.get('cliente'), variables_map.get('ambiente'))

        # Valid network_version - IPv4
        if network_version == IP_VERSION.IPv4[0]:

            # Find IpEquipamento to check if it exist
            IpEquip = IpEquipamento().get_by_ip_equipment(ip_id, equip_id)

            real_name = IpEquip.equipamento.nome
            end_ip = '%s.%s.%s.%s' % (
                IpEquip.ip.oct1, IpEquip.ip.oct2, IpEquip.ip.oct3, IpEquip.ip.oct4)

            # Valid Real
            RequisicaoVips.valid_real_server(
                end_ip, IpEquip.equipamento, evip, False)

        # Valid network_version - IPv6
        elif network_version == IP_VERSION.IPv6[0]:

            # Find Ipv6Equipament to check if it exist
            Ipv6Equip = Ipv6Equipament().get_by_ip_equipment(ip_id, equip_id)

            real_name = Ipv6Equip.equipamento.nome
            end_ip = '%s:%s:%s:%s:%s:%s:%s:%s' % (Ipv6Equip.ip.block1, Ipv6Equip.ip.block2, Ipv6Equip.ip.block3,
                                                  Ipv6Equip.ip.block4, Ipv6Equip.ip.block5, Ipv6Equip.ip.block6, Ipv6Equip.ip.block7, Ipv6Equip.ip.block8)

            # Valid Real
            RequisicaoVips.valid_real_server(
                end_ip, Ipv6Equip.equipamento, evip, False)

        if (operation == 'chk'):

            if IP_VERSION.IPv4[0] == network_version:
                if new_call:
                    command = VIP_REALS_v4_CHECK % (
                        vip_id, ip_id, port_real, port_vip)
                else:
                    command = VIP_REAL_v4_CHECK % (vip_id, real_name, end_ip)
            else:
                if new_call:
                    command = VIP_REALS_v6_CHECK % (
                        vip_id, ip_id, port_real, port_vip)
                else:
                    command = VIP_REAL_v6_CHECK % (vip_id, real_name, end_ip)
        else:

            with distributedlock(LOCK_VIP_IP_EQUIP % (vip_id, ip_id, equip_id)):

                if (operation == 'add'):

                    if IP_VERSION.IPv4[0] == network_version:
                        if new_call:
                            command = VIP_REALS_v4_CREATE % (
                                vip_id, ip_id, port_real, port_vip)
                            ServerPoolMember().save_specified_port(
                                vip_id, port_vip, IpEquip.ip, IP_VERSION.IPv4[1], port_real, user)
                        else:
                            command = VIP_REAL_v4_CREATE % (
                                vip_id, real_name, end_ip)
                            ServerPoolMember().save_with_default_port(
                                vip_id, IpEquip.ip, IP_VERSION.IPv4[1], user)

                    else:
                        if new_call:
                            command = VIP_REALS_v6_CREATE % (
                                vip_id, ip_id, port_real, port_vip)
                            ServerPoolMember().save_specified_port(
                                vip_id, port_vip, Ipv6Equip.ip, IP_VERSION.IPv6[1], port_real, user)
                        else:
                            command = VIP_REAL_v6_CREATE % (
                                vip_id, real_name, end_ip)
                            ServerPoolMember().save_with_default_port(
                                vip_id, Ipv6Equip.ip, IP_VERSION.IPv6[1], user)

                elif (operation == 'del'):

                    if IP_VERSION.IPv4[0] == network_version:
                        if new_call:
                            command = VIP_REALS_v4_REMOVE % (
                                vip_id, ip_id, port_real, port_vip)
                            pool_members = ServerPoolMember.objects.filter(
                                ip=ip_id, server_pool__vipporttopool__requisicao_vip__id=vip_id, server_pool__vipporttopool__port_vip=port_vip, port_real=port_real)
                            [pool_member.delete()
                             for pool_member in pool_members]
                        else:
                            command = VIP_REAL_v4_REMOVE % (
                                vip_id, real_name, end_ip)
                            pool_members = ServerPoolMember.objects.filter(
                                ip=ip_id, server_pool__vipporttopool__requisicao_vip__id=vip_id)
                            [pool_member.delete()
                             for pool_member in pool_members]
                    else:
                        if new_call:
                            command = VIP_REALS_v6_REMOVE % (
                                vip_id, ip_id, port_real, port_vip)
                            pool_members = ServerPoolMember.objects.filter(
                                ipv6=ip_id, server_pool__vipporttopool__requisicao_vip__id=vip_id, server_pool__vipporttopool__port_vip=port_vip, port_real=port_real)
                            [pool_member.delete()
                             for pool_member in pool_members]
                        else:
                            command = VIP_REAL_v6_REMOVE % (
                                vip_id, real_name, end_ip)
                            pool_members = ServerPoolMember.objects.filter(
                                ipv6=ip_id, server_pool__vipporttopool__requisicao_vip__id=vip_id)
                            [pool_member.delete()
                             for pool_member in pool_members]

                elif (operation == 'ena'):

                    if IP_VERSION.IPv4[0] == network_version:
                        if new_call:
                            command = VIP_REALS_v4_ENABLE % (
                                vip_id, ip_id, port_real, port_vip)
                        else:
                            command = VIP_REAL_v4_ENABLE % (
                                vip_id, real_name, end_ip)
                    else:
                        if new_call:
                            command = VIP_REALS_v6_ENABLE % (
                                vip_id, ip_id, port_real, port_vip)
                        else:
                            command = VIP_REAL_v6_ENABLE % (
                                vip_id, real_name, end_ip)

                elif (operation == 'dis'):

                    if IP_VERSION.IPv4[0] == network_version:
                        if new_call:
                            command = VIP_REALS_v4_DISABLE % (
                                vip_id, ip_id, port_real, port_vip)
                        else:
                            command = VIP_REAL_v4_DISABLE % (
                                vip_id, real_name, end_ip)
                    else:
                        if new_call:
                            command = VIP_REALS_v6_DISABLE % (
                                vip_id, ip_id, port_real, port_vip)
                        else:
                            command = VIP_REAL_v6_DISABLE % (
                                vip_id, real_name, end_ip)

        self.log.info(command)
        # Execute script
        code, stdout, stderr = exec_script(command)
        self.log.info(stdout)

        map = dict()
        success_map = dict()

        # Return XML
        if code == 0:
            success_map['codigo'] = '%04d' % code
            success_map['descricao'] = {'stdout': stdout, 'stderr': stderr}

            map['sucesso'] = success_map
            return self.response(dumps_networkapi(map))

        elif code == 12:
            success_map['codigo'] = '0'
            success_map['descricao'] = {'stdout': '0', 'stderr': ''}

            map['sucesso'] = success_map
            self.rollback_changes(operation, new_call, network_version,
                                  vip_id, ip_id, port_real, port_vip, real_name, end_ip, user)
            return self.response(dumps_networkapi(map))

        else:
            self.rollback_changes(operation, new_call, network_version,
                                  vip_id, ip_id, port_real, port_vip, real_name, end_ip, user)
            return self.response_error(2, stdout + stderr)

    def rollback_changes(self, operation, new_call, network_version, vip_id, ip_id, port_real, port_vip, real_name, end_ip, user):
        if (operation == 'add'):  # So remove the item that was inserted
            if IP_VERSION.IPv4[0] == network_version:
                if IP_VERSION.IPv4[0] == network_version:
                    if new_call:
                        pool_members = ServerPoolMember.objects.filter(
                            ip=ip_id, server_pool__vipporttopool__requisicao_vip__id=vip_id, server_pool__vipporttopool__port_vip=port_vip, port_real=port_real)
                        [pool_member.delete()
                         for pool_member in pool_members]
                    else:
                        pool_members = ServerPoolMember.objects.filter(
                            ip=ip_id, server_pool__vipporttopool__requisicao_vip__id=vip_id)
                        [pool_member.delete()
                         for pool_member in pool_members]
                else:
                    if new_call:
                        pool_members = ServerPoolMember.objects.filter(
                            ipv6=ip_id, server_pool__vipporttopool__requisicao_vip__id=vip_id, server_pool__vipporttopool__port_vip=port_vip, port_real=port_real)
                        [pool_member.delete()
                         for pool_member in pool_members]
                    else:
                        pool_members = ServerPoolMember.objects.filter(
                            ipv6=ip_id, server_pool__vipporttopool__requisicao_vip__id=vip_id)
                        [pool_member.delete()
                         for pool_member in pool_members]
            # commit to rollback when script return error
            transaction.commit()
