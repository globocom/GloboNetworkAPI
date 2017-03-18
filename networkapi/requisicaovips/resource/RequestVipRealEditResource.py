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
from networkapi.distributedlock import LOCK_VIP
from networkapi.equipamento.models import Equipamento
from networkapi.equipamento.models import EquipamentoError
from networkapi.equipamento.models import EquipamentoNotFoundError
from networkapi.exception import EquipmentGroupsNotAuthorizedError
from networkapi.exception import InvalidValueError
from networkapi.exception import RequestVipsNotBeenCreatedError
from networkapi.grupo.models import GrupoError
from networkapi.healthcheckexpect.models import HealthcheckExpectError
from networkapi.healthcheckexpect.models import HealthcheckExpectNotFoundError
from networkapi.infrastructure.script_utils import exec_script
from networkapi.infrastructure.script_utils import ScriptError
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.infrastructure.xml_utils import loads
from networkapi.infrastructure.xml_utils import XMLError
from networkapi.ip.models import Ip
from networkapi.ip.models import IpEquipmentNotFoundError
from networkapi.ip.models import IpError
from networkapi.ip.models import IpNotFoundByEquipAndVipError
from networkapi.ip.models import IpNotFoundError
from networkapi.ip.models import Ipv6
from networkapi.requisicaovips.models import InvalidAmbienteValueError
from networkapi.requisicaovips.models import InvalidBalAtivoValueError
from networkapi.requisicaovips.models import InvalidCacheValueError
from networkapi.requisicaovips.models import InvalidClienteValueError
from networkapi.requisicaovips.models import InvalidFinalidadeValueError
from networkapi.requisicaovips.models import InvalidHealthcheckTypeValueError
from networkapi.requisicaovips.models import InvalidHealthcheckValueError
from networkapi.requisicaovips.models import InvalidHostNameError
from networkapi.requisicaovips.models import InvalidMaxConValueError
from networkapi.requisicaovips.models import InvalidMetodoBalValueError
from networkapi.requisicaovips.models import InvalidPersistenciaValueError
from networkapi.requisicaovips.models import InvalidPriorityValueError
from networkapi.requisicaovips.models import InvalidRealValueError
from networkapi.requisicaovips.models import InvalidServicePortValueError
from networkapi.requisicaovips.models import InvalidTimeoutValueError
from networkapi.requisicaovips.models import InvalidTransbordoValueError
from networkapi.requisicaovips.models import RequisicaoVips
from networkapi.requisicaovips.models import RequisicaoVipsError
from networkapi.requisicaovips.models import RequisicaoVipsNotFoundError
from networkapi.requisicaovips.models import ServerPool
from networkapi.requisicaovips.models import ServerPoolMember
from networkapi.requisicaovips.models import VipPortToPool
from networkapi.rest import RestResource
from networkapi.rest import UserNotAuthorizedError
from networkapi.settings import VIP_REAL_v4_CREATE
from networkapi.settings import VIP_REAL_v4_REMOVE
from networkapi.settings import VIP_REAL_v6_CREATE
from networkapi.settings import VIP_REAL_v6_REMOVE
from networkapi.settings import VIP_REALS_v4_CREATE
from networkapi.settings import VIP_REALS_v4_REMOVE
from networkapi.settings import VIP_REALS_v6_CREATE
from networkapi.settings import VIP_REALS_v6_REMOVE
from networkapi.util import clone
from networkapi.util import is_valid_int_greater_equal_zero_param
from networkapi.util import is_valid_int_greater_zero_param
from networkapi.util import is_valid_ipv4
from networkapi.util.decorators import deprecated


class RequestVipRealEditResource(RestResource):

    log = logging.getLogger('RequestVipRealEditResource')

    @deprecated(new_uri='check uri to edit pool')
    def handle_put(self, request, user, *args, **kwargs):
        """
        Handles PUT requests to change the VIP's real server.

        URL: vip/real/edit
        """

        self.log.info("Change VIP's real server")

        try:

            # User permission
            if not has_perm(user, AdminPermission.VIP_ALTER_SCRIPT, AdminPermission.WRITE_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                raise UserNotAuthorizedError(None)

            # Commons Validations

            # Load XML data
            xml_map, attrs_map = loads(
                request.raw_post_data, ['real', 'reals_weight', 'reals_priority'])

            # XML data format
            networkapi_map = xml_map.get('networkapi')
            if networkapi_map is None:
                return self.response_error(3, u'There is no value to the networkapi tag  of XML request.')

            vip_map = networkapi_map.get('vip')
            if vip_map is None:
                return self.response_error(3, u'There is no value to the vip tag  of XML request.')

            # Get XML data
            vip_id = vip_map.get('vip_id')
            alter_priority = vip_map.get('alter_priority')

            # Valid VIP ID
            if not is_valid_int_greater_zero_param(vip_id):
                self.log.error(
                    u'The vip_id parameter is not a valid value: %s.', vip_id)
                raise InvalidValueError(None, 'vip_id', vip_id)

            # Valid Alter Priority
            if not is_valid_int_greater_equal_zero_param(alter_priority):
                alter_priority = 0

            # Existing Vip ID
            vip = RequisicaoVips.get_by_pk(vip_id)

            # Clone vip
            vip_old = clone(vip)

            server_pools = ServerPool.objects.filter(
                vipporttopool__requisicao_vip=vip)
            server_pools_old = []
            server_pools_members_old = []
            for sp in server_pools:
                server_pools_old.append(sp)
                for spm in sp.serverpoolmember_set.all():
                    server_pools_members_old.append(spm)

            # Get variables
            variables_map = vip.variables_to_map()

            # Valid variables
            vip.set_variables(variables_map)

            # Get balancing method
            vip_map['metodo_bal'] = str(
                variables_map.get('metodo_bal')).upper()

            with distributedlock(LOCK_VIP % vip_id):

                # Valid real names and real ips of real server
                if vip_map.get('reals') is not None:

                    evip = EnvironmentVip.get_by_values(variables_map.get(
                        'finalidade'), variables_map.get('cliente'), variables_map.get('ambiente'))

                    for real in vip_map.get('reals').get('real'):
                        ip_aux_error = real.get('real_ip')
                        equip_aux_error = real.get('real_name')
                        if equip_aux_error is not None:
                            equip = Equipamento.get_by_name(equip_aux_error)
                        else:
                            self.log.error(
                                u'The real_name parameter is not a valid value: None.')
                            raise InvalidValueError(None, 'real_name', 'None')

                        # Valid Real
                        RequisicaoVips.valid_real_server(
                            ip_aux_error, equip, evip, False)

                    # Valid reals_prioritys
                    vip_map, code = vip.valid_values_reals_priority(vip_map)
                    if code is not None:
                        return self.response_error(329)

                    # Valid reals_weight
                    vip_map, code = vip.valid_values_reals_weight(vip_map)
                    if code is not None:
                        return self.response_error(330)

                # Get variables
                variables_map = vip.variables_to_map()

                vip_port_list, reals_list, reals_priority, reals_weight = vip.get_vips_and_reals(
                    vip.id)

                if reals_list:
                    variables_map['reals'] = {'real': reals_list}
                    variables_map['reals_prioritys'] = {
                        'reals_priority': reals_priority}
                    variables_map['reals_weights'] = {
                        'reals_weight': reals_weight}

                variables_map['portas_servicos'] = {'porta': vip_port_list}

                # clone variables_map
                # variables_map_old = clone(variables_map)

                # Valid ports
                variables_map, code = vip.valid_values_ports(variables_map)
                if code is not None:
                    return self.response_error(331)

                """ OLD CALLS - Deprecated """
                vip_ports_pool = VipPortToPool.objects.filter(
                    requisicao_vip=vip)

                reals = vip_map.get('reals')

                new_call = True
                if reals and 'port_real' not in reals['real'][0]:
                    new_call = False
                    reals_prioritys = vip_map.get('reals_prioritys')
                    reals_weights = dict()
                    if 'reals_weights' in vip_map:
                        reals_weights = vip_map.get('reals_weights')

                    reals_aux = dict()
                    reals_prioritys_aux = dict()
                    reals_weight_aux = dict()

                    reals_aux['real'] = list()
                    reals_prioritys_aux['reals_priority'] = list()
                    reals_weight_aux['reals_weight'] = list()

                    repeat = (
                        len(vip_ports_pool) * len(reals['real'])) / len(reals['real'])
                    execute_list = list()

                    for x in range(repeat):
                        execute_list.append((x + 1) * len(reals['real']))

                    for i in range(len(reals['real'])):
                        for vippp in vip_ports_pool:

                            reals_prioritys_aux['reals_priority'].append(
                                reals_prioritys['reals_priority'][i])
                            if 'reals_weight' in reals_weights:
                                reals_weight_aux['reals_weight'].append(
                                    reals_weights['reals_weight'][i])
                            server_pool = ServerPool.objects.get(
                                vipporttopool__id=vippp.id, vipporttopool__requisicao_vip=vip)

                            if 'id_ip' not in reals['real'][i]:
                                id_ip = get_id_ip(reals['real'][i])
                            else:
                                id_ip = reals['real'][i]['id_ip']

                            reals_aux['real'].append({'id_ip': id_ip, 'port_real': server_pool.default_port, 'real_name': reals[
                                                     'real'][i]['real_name'], 'port_vip': vippp.port_vip, u'real_ip': reals['real'][i]['real_ip']})

                        vip_map['reals_prioritys'] = reals_prioritys_aux
                        vip_map['reals_weights'] = reals_weight_aux
                        vip_map['reals'] = reals_aux

                """ OLD CALLS - END """

                # Check diff reals (reals_to_add, reals_to_rem, reals_to_stay)
                reals_to_add, reals_to_rem, reals_to_stay = diff_reals(
                    variables_map, vip_map)

                reals_final = dict()
                reals_final['reals'] = list()
                reals_final['priorities'] = list()
                reals_final['weights'] = list()

                reals_error = list()
                removes = True
                error = False

                ##############################################
                #        NOT MODIFIED - reals_to_stay        #
                ##############################################
                for i in range(len(reals_to_stay['reals'])):

                    real, priority, weight, id_ip, port_vip, port_real, new_call = get_variables(
                        reals_to_stay, i, new_call)

                    # Check ip type
                    if is_valid_ipv4(real.get('real_ip')) is True:
                        ip_type = IP_VERSION.IPv4[1]
                        ip = Ip().get_by_pk(id_ip)
                    else:
                        ip_type = IP_VERSION.IPv6[1]
                        ip = Ipv6().get_by_pk(id_ip)

                    reals_final['reals'].append(reals_to_stay['reals'][i])
                    reals_final['priorities'].append(
                        reals_to_stay['priorities'][i])
                    if reals_to_stay['weighted']:
                        reals_final['weights'].append(
                            reals_to_stay['weights'][i])

                        server_pool = ServerPool.objects.get(
                            vipporttopool__port_vip=port_vip, vipporttopool__requisicao_vip=vip)
                        if ip_type == IP_VERSION.IPv4[1]:
                            server_pool_member = ServerPoolMember.objects.get(server_pool=server_pool,
                                                                              port_real=port_real,
                                                                              ip=id_ip)
                        else:
                            server_pool_member = ServerPoolMember.objects.get(server_pool=server_pool,
                                                                              port_real=port_real,
                                                                              ipv6=id_ip)
                    server_pool_member.priority = priority
                    server_pool_member.weight = weight
                    server_pool_member.save(user, commit=True)

                #############################################
                #          ADD REALS - reals_to_add         #
                #############################################
                for i in range(len(reals_to_add['reals'])):

                    real, priority, weight, id_ip, port_vip, port_real, new_call = get_variables(
                        reals_to_add, i, new_call)

                    if len(real.get('real_ip').split('.')) <= 1:
                        ip_type = IP_VERSION.IPv6[1]
                        ip = Ipv6().get_by_pk(id_ip)
                        if new_call:
                            command = VIP_REALS_v6_CREATE % (
                                vip.id, id_ip, port_real, port_vip)
                        else:
                            command = VIP_REAL_v6_CREATE % (
                                vip.id, real.get('real_name'), real.get('real_ip'))
                    else:
                        ip_type = IP_VERSION.IPv4[1]
                        ip = Ip().get_by_pk(id_ip)
                        if new_call:
                            command = VIP_REALS_v4_CREATE % (
                                vip.id, id_ip, port_real, port_vip)
                        else:
                            command = VIP_REAL_v4_CREATE % (
                                vip.id, real.get('real_name'), real.get('real_ip'))

                    self.log.info(
                        '------------------- ADD ----------------------')
                    self.log.info(
                        'Insert ServerPoolMember before execute script')

                    add_reals_before_script(
                        port_vip, vip, ip, ip_type, priority, weight, port_real, user)

                    self.log.info('The insert has completed successfully')

                    # if new_call or (i + 1) in execute_list:

                    self.log.info('Execute script: %s' % command)

                    code, stdout, stderr = exec_script(command)

                    self.log.info(
                        'Script was executed and returned code %s' % code)

                    if code != 0:
                        removes = False
                        error = True
                        reals_error.append(real)

                        self.log.info(
                            'Remove ServerPoolMember after execute script if code != 0')
                        remove_reals_after_script(
                            port_vip, ip_type, vip, port_real, priority, weight, id_ip, user)
                        self.log.info('The remove has completed successfully')

                    else:
                        reals_final['reals'].append(real)
                        reals_final['priorities'].append(
                            reals_to_add['priorities'][i])
                        if reals_to_add['weighted']:
                            reals_final['weights'].append(
                                reals_to_add['weights'][i])

                    self.log.info(
                        '----------------- ADD END --------------------')

                ##########################################
                #       REMOVE REALS - reals_to_rem      #
                ##########################################
                if removes:
                    for i in range(len(reals_to_rem['reals'])):

                        real, priority, weight, id_ip, port_vip, port_real, new_call = get_variables(
                            reals_to_rem, i, new_call)

                        if len(real.get('real_ip').split('.')) <= 1:
                            ip_type = IP_VERSION.IPv6[1]
                            if new_call:
                                command = VIP_REALS_v6_REMOVE % (
                                    vip.id, id_ip, port_real, port_vip)
                            else:
                                command = VIP_REAL_v6_REMOVE % (
                                    vip.id, real.get('real_name'), real.get('real_ip'))
                        else:
                            ip_type = IP_VERSION.IPv4[1]
                            if new_call:
                                command = VIP_REALS_v4_REMOVE % (
                                    vip.id, id_ip, port_real, port_vip)
                            else:
                                command = VIP_REAL_v4_REMOVE % (
                                    vip.id, real.get('real_name'), real.get('real_ip'))

                        self.log.info(
                            '------------------ REMOVE --------------------')
                        self.log.info('Execute script: %s' % command)

                        code, stdout, stderr = exec_script(command)

                        self.log.info(
                            'script was executed and returned code %s' % code)

                        if code != 0:
                            error = True
                            reals_error.append(real)
                            reals_final['reals'].append(real)
                            reals_final['priorities'].append(
                                reals_to_rem['priorities'][i])
                            if reals_to_rem['weighted']:
                                reals_final['weights'].append(
                                    reals_to_rem['weights'][i])
                        else:

                            self.log.info(
                                'Remove ServerPoolMember after execute script')
                            remove_reals_after_script(
                                port_vip, ip_type, vip, port_real, priority, weight, id_ip, user)
                            self.log.info(
                                'The remove has completed successfully')

                        self.log.info(
                            '---------------- REMOVE END ------------------')

                else:
                    for i in range(len(reals_to_rem['reals'])):
                        real = reals_to_rem['reals'][i]
                        reals_final['reals'].append(real)
                        reals_final['priorities'].append(
                            reals_to_rem['priorities'][i])
                        if reals_to_add['weighted']:
                            reals_final['weights'].append(
                                reals_to_rem['weights'][i])

                variables_map['reals'] = dict()
                variables_map['reals_prioritys'] = dict()
                variables_map['reals_weights'] = dict()

                if len(reals_final['reals']) > 0:
                    variables_map['reals']['real'] = reals_final['reals']
                    variables_map['reals_prioritys'][
                        'reals_priority'] = reals_final['priorities']
                    if reals_final['weights'] is not None:
                        variables_map['reals_weights'][
                            'reals_weight'] = reals_final['weights']
                else:
                    variables_map.pop('reals')
                    variables_map.pop('reals_prioritys')
                    variables_map.pop('reals_weights')

                # set variables
                vip.set_variables(variables_map)

                try:
                    # If Priority changed
                    if int(alter_priority) != 0:
                        # gerador_vips -i <ID_REQUISICAO> --priority
                        command = 'gerador_vips -i %d --priority' % vip.id

                        # Logging
                        self.log.info(
                            '---------------- ALTER PRIORITY ------------------')
                        self.log.info('Command: ' + command)

                        # Execute script
                        code, stdout, stderr = exec_script(command)
                        self.log.info('Code returned: ' + str(code))
                        self.log.info('Stdout: ' + stdout)
                        self.log.info(
                            '-------------- ALTER PRIORITY END ----------------')

                        # Script returned error while executing, rollback the
                        # changes in database
                        if code != 0:
                            self.log.info('Code != 0, rollback changes')
                            vip_old.save(user, commit=True)
                            for sp in server_pools_old:
                                sp.save(user, commit=True)
                            for spm in server_pools_members_old:
                                spm.save(user, commit=True)

                            return self.response_error(2, stdout + stderr)

                except Exception, e:
                    if isinstance(e, IntegrityError):
                        # Duplicate value for Port Vip, Port Real and IP
                        self.log.error(u'Failed to update the request vip.')
                        return self.response_error(353)
                    else:
                        self.log.error(u'Failed to update the request vip.')
                        raise RequisicaoVipsError(
                            e, u'Failed to update the request vip')

                if error:
                    # build return message
                    vip_list = ''
                    ip_list = ''

                    for real in reals_error:
                        vip_list = vip_list + real['real_name'] + ', '
                        ip_list = ip_list + real['real_ip'] + ', '

                    return self.response_error(333, vip_list[:-2], ip_list[:-2])
                else:
                    return self.response(dumps_networkapi({}))

        except XMLError, x:
            self.log.error(u'Error reading the XML request.')
            return self.response_error(3, x)
        except ScriptError, s:
            return self.response_error(2, s)
        except EquipmentGroupsNotAuthorizedError:
            return self.response_error(271)
        except RequestVipsNotBeenCreatedError:
            return self.response_error(270, vip_id)
        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)
        except IpNotFoundError:
            return self.response_error(328, ip_aux_error, equip_aux_error)
        except HealthcheckExpectNotFoundError:
            return self.response_error(124)
        except RequisicaoVipsNotFoundError:
            return self.response_error(152)
        except InvalidFinalidadeValueError:
            return self.response_error(125)
        except InvalidClienteValueError:
            return self.response_error(126)
        except InvalidAmbienteValueError:
            return self.response_error(127)
        except InvalidCacheValueError:
            return self.response_error(128)
        except InvalidMetodoBalValueError:
            return self.response_error(131)
        except InvalidPersistenciaValueError:
            return self.response_error(132)
        except InvalidHealthcheckTypeValueError:
            return self.response_error(133)
        except InvalidPriorityValueError:
            return self.response_error(325)
        except EquipamentoNotFoundError, e:
            return self.response_error(326, equip_aux_error)
        except IpEquipmentNotFoundError:
            return self.response_error(327, ip_aux_error, equip_aux_error)
        except InvalidHealthcheckValueError:
            return self.response_error(134)
        except InvalidTimeoutValueError:
            return self.response_error(135)
        except InvalidHostNameError:
            return self.response_error(136)
        except InvalidMaxConValueError:
            return self.response_error(137)
        except InvalidServicePortValueError, e:
            porta = 'nulo'
            if e.message is not None:
                porta = e.message
            return self.response_error(138, porta)
        except InvalidRealValueError, e:
            real = 'nulo'
            if e.message is not None:
                real = e.message
            return self.response_error(151, real)
        except InvalidBalAtivoValueError:
            return self.response_error(129)
        except InvalidTransbordoValueError, e:
            transbordo = 'nulo'
            if e.message is not None:
                transbordo = e.message
            return self.response_error(130, transbordo)
        except UserNotAuthorizedError:
            return self.not_authorized()
        except IpNotFoundByEquipAndVipError:
            return self.response_error(334, e.message)
        except (RequisicaoVipsError, EquipamentoError, IpError, HealthcheckExpectError, GrupoError), e:
            return self.response_error(1)
        except Exception, e:
            self.log.error(u'Failed to update the request vip.')
            if isinstance(e, IntegrityError):
                # Duplicate value for Port Vip, Port Real and IP
                return self.response_error(353)
            else:
                raise RequisicaoVipsError(
                    e, u'Failed to update the request vip')


def get_variables(map, i, new_call):
    """
        Initialize variables
    """

    real = map['reals'][i]
    priority = map['priorities'][i]
    if map['weighted']:
        weight = map['weights'][i]
    else:
        if new_call is False:
            weight = 1
        else:
            weight = 0

    if new_call is False:
        id_ip = get_id_ip(real)
    else:
        id_ip = real.get('id_ip')

    if 'port_vip' in real and 'port_real' in real:
        port_vip = real.get('port_vip')
        port_real = real.get('port_real')

    # if port_vip is not None and port_real is not None:
    #    new_call = True

    return real, priority, weight, id_ip, port_vip, port_real, new_call


def get_id_ip(real):
    """
        Get real id_ip by octs/block and equipment
    """
    equip = Equipamento().get_by_name(real['real_name'])

    # Check ip type
    if is_valid_ipv4(real['real_ip']) is True:
        oct = real['real_ip'].split('.')
        ip = Ip().get_by_octs_equipment(
            oct[0], oct[1], oct[2], oct[3], equip.id)
    else:
        block = real['real_ip'].split(':')
        ip = Ipv6().get_by_blocks_equipment(block[0], block[1], block[2], block[
            3], block[4], block[5], block[6], block[7], equip.id)

    return ip.id


def add_reals_before_script(port_vip, vip, ip, ip_type, priority, weight, port_real, user):
    """
        Add real in VIP before execute script.
        The script access the db when is executing.
        This method is called if code returns 0.
    """

    server_pool_member = ServerPoolMember()
    server_pool = ServerPool.objects.get(
        vipporttopool__port_vip=port_vip, vipporttopool__requisicao_vip=vip)
    server_pool_member.prepare_and_save(
        server_pool, ip, ip_type, priority, weight, port_real, user, True)


def remove_reals_after_script(port_vip, ip_type, vip, port_real, priority, weight, id_ip, user):
    """
        Remove real in VIP if script was completed successfully.
        The script access the db when is executing.
        This method is called if code returns 0.
    """

    server_pool = ServerPool.objects.get(
        vipporttopool__port_vip=port_vip, vipporttopool__requisicao_vip=vip)
    if ip_type == IP_VERSION.IPv4[1]:
        server_pool_member = ServerPoolMember.objects.get(server_pool=server_pool,
                                                          port_real=port_real,
                                                          priority=priority,
                                                          weight=weight,
                                                          ip=id_ip)
    else:
        server_pool_member = ServerPoolMember.objects.get(server_pool=server_pool,
                                                          port_real=port_real,
                                                          priority=priority,
                                                          weight=weight,
                                                          ipv6=id_ip)
    server_pool_member.delete()
    transaction.commit()


def diff_reals(old_map, new_map):

    old_reals = None
    old_priorities = None
    old_weights = None

    new_reals = None
    new_priorities = None
    new_weights = None

    if 'reals' in old_map:
        old_reals = old_map.get('reals')
        old_priorities = old_map.get('reals_prioritys')
        old_weights = old_map.get('reals_weights')
    if old_reals is not None:
        old_reals = old_reals.get('real')

        old_reals_list = list()
        for o_real in old_reals:
            old_reals_list.append({'id_ip': unicode(o_real['id_ip']), 'port_real': unicode(o_real['port_real']), 'real_name': unicode(
                o_real['real_name']), 'port_vip': unicode(o_real['port_vip']), 'real_ip': unicode(o_real['real_ip'])})

        old_reals = old_reals_list
    if old_priorities is not None:
        old_priorities = old_priorities.get('reals_priority')
        old_priorities = [str(x) for x in old_priorities]
    if old_weights is not None:
        old_weights = old_weights.get('reals_weight')
        old_weights = [str(x) for x in old_weights]

    if 'reals' in new_map:
        new_reals = new_map.get('reals')
        new_priorities = new_map.get('reals_prioritys')
        new_weights = new_map.get('reals_weights')
    if new_reals is not None:
        new_reals = new_reals.get('real')

        new_reals_list = list()
        for n_real in new_reals:
            new_reals_list.append({'id_ip': unicode(n_real['id_ip']), 'port_real': unicode(n_real['port_real']), 'real_name': unicode(
                n_real['real_name']), 'port_vip': unicode(n_real['port_vip']), 'real_ip': unicode(n_real['real_ip'])})

        new_reals = new_reals_list

    if new_priorities is not None:
        new_priorities = new_priorities.get('reals_priority')
    if new_weights is not None:
        new_weights = new_weights.get('reals_weight')
        if len(new_weights) == 0 or len(new_weights) != len(new_priorities):
            new_weights = None

    weights = True
    if new_weights is None and old_weights is None:
        weights = False

    to_add = dict()
    to_rem = dict()
    to_stay = dict()

    to_add['reals'] = list()
    to_add['priorities'] = list()
    to_add['weights'] = list()
    to_add['weighted'] = weights

    to_rem['reals'] = list()
    to_rem['priorities'] = list()
    to_rem['weights'] = list()
    to_rem['weighted'] = weights

    to_stay['reals'] = list()
    to_stay['priorities'] = list()
    to_stay['weights'] = list()
    to_stay['weighted'] = weights

    if old_reals is None and new_reals is None:
        return to_add, to_rem, to_stay

    if old_reals is not None:
        for index in range(len(old_reals)):
            real = old_reals[index]
            if new_reals is not None:
                if real not in new_reals:
                    to_rem['reals'].append(real)
                    to_rem['priorities'].append(old_priorities[index])
                    if weights:
                        to_rem['weights'].append(old_weights[index])
                else:
                    to_stay['reals'].append(real)
                    to_stay['priorities'].append(
                        new_priorities[new_reals.index(real)])
                    if weights:
                        to_stay['weights'].append(
                            new_weights[new_reals.index(real)] if new_weights else 0)
            else:
                to_rem['reals'].append(real)
                to_rem['priorities'].append(old_priorities[index])
                if weights:
                    to_rem['weights'].append(old_weights[index])

    if new_reals is not None:
        for index in range(len(new_reals)):
            real = new_reals[index]
            if old_reals is not None:
                if real not in old_reals:
                    to_add['reals'].append(real)
                    to_add['priorities'].append(new_priorities[index])
                    if weights:
                        to_add['weights'].append(
                            new_weights[index] if new_weights else 0)
            else:
                to_add['reals'].append(real)
                to_add['priorities'].append(new_priorities[index])
                if weights:
                    to_add['weights'].append(new_weights[index])

    return to_add, to_rem, to_stay
