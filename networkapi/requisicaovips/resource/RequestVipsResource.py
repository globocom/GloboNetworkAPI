# -*- coding:utf-8 -*-

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
from networkapi.rest import RestResource, UserNotAuthorizedError
from networkapi.admin_permission import AdminPermission
from networkapi.requisicaovips.models import RequisicaoVips, RequisicaoVipsError, InvalidFinalidadeValueError, InvalidClienteValueError, \
    InvalidAmbienteValueError, InvalidCacheValueError, InvalidMetodoBalValueError, InvalidPersistenciaValueError, \
    InvalidHealthcheckTypeValueError, InvalidHealthcheckValueError, InvalidTimeoutValueError, InvalidHostNameError, \
    InvalidMaxConValueError, InvalidServicePortValueError, InvalidRealValueError, RequisicaoVipsAlreadyCreatedError, RequisicaoVipsNotFoundError, \
    InvalidBalAtivoValueError, InvalidTransbordoValueError
from networkapi.equipamento.models import EquipamentoError, Equipamento, EquipamentoNotFoundError
from networkapi.ip.models import Ip, Ipv6, IpNotFoundError, IpError, IpEquipmentNotFoundError, IpNotFoundByEquipAndVipError
from networkapi.ambiente.models import EnvironmentVip, Ambiente
from networkapi.healthcheckexpect.models import HealthcheckExpectError, HealthcheckExpectNotFoundError
from networkapi.grupo.models import GrupoError
from networkapi.auth import has_perm
from networkapi.infrastructure.xml_utils import loads, dumps_networkapi
from networkapi.log import Log
from networkapi.util import is_valid_boolean_param, is_valid_int_greater_equal_zero_param, is_valid_int_greater_zero_param, \
    is_valid_ipv4, is_valid_string_minsize, is_valid_string_maxsize, \
    is_valid_list_int_greater_zero_param
from networkapi.exception import InvalidValueError, EnvironmentVipNotFoundError
from networkapi.distributedlock import distributedlock, LOCK_VIP
from networkapi.requisicaovips.models import VipPortToPool
from networkapi.requisicaovips.models import ServerPool, ServerPoolMember
from django.db.utils import IntegrityError
from django.db.models import Q
from networkapi.blockrules.models import Rule
from networkapi.error_message_utils import error_messages


class RequestVipsResource(RestResource):

    log = Log('RequestVipsResource')

    def handle_post(self, request, user, *args, **kwargs):
        """Treat requests POST to insert request VIP.

        URLs: /requestvip/
        """
        self.log.info("Add request VIP")

        try:
            # Load XML data
            xml_map, attrs_map = loads(request.raw_post_data, ['pool_ids'])

            # XML data format

            networkapi_map = xml_map.get('networkapi')
            if networkapi_map is None:
                return self.response_error(3, u'There is no value to the networkapi tag  of XML request.')

            vip_map = networkapi_map.get('vip')
            if vip_map is None:
                return self.response_error(3, u'There is no value to the vip tag  of XML request.')

            # User permission
            if not has_perm(user, AdminPermission.VIPS_REQUEST, AdminPermission.WRITE_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                raise UserNotAuthorizedError(None)

            # Valid Ipv4 and Ipv6 ID
            if (vip_map.get('id_ipv4') is None and vip_map.get('id_ipv6') is None):
                self.log.error(
                    u'The id_ipv4 and id_ipv6 parameter is not a valid value: %s.', vip_map.get('id_ipv4'))
                raise InvalidValueError(
                    None, 'id_ipv4 e id_vip6', vip_map.get('id_ipv4'))

            if (vip_map.get('id_ipv4') != None):
                if not is_valid_int_greater_zero_param(vip_map.get('id_ipv4')):
                    self.log.error(
                        u'The id_ipv4 parameter is not a valid value: %s.', vip_map.get('id_ipv4'))
                    raise InvalidValueError(
                        None, 'id_ipv4', vip_map.get('id_ipv4'))

            if (vip_map.get('id_ipv6') != None):
                if not is_valid_int_greater_zero_param(vip_map.get('id_ipv6')):
                    self.log.error(
                        u'The id_ipv6 parameter is not a valid value: %s.', vip_map.get('id_ipv6'))
                    raise InvalidValueError(
                        None, 'id_ipv6', vip_map.get('id_ipv6'))

            pool_ids = vip_map.get('pool_ids')

            vip = RequisicaoVips()

            finalidade = vip_map.get('finalidade')
            cliente = vip_map.get('cliente')
            ambiente = vip_map.get('ambiente')

            try:
                evip = EnvironmentVip.get_by_values(
                    finalidade, cliente, ambiente)
            except Exception, e:
                raise EnvironmentVipNotFoundError(
                    e, 'The fields finality or client or ambiente is None')


            # Existing IPv4 ID
            if vip_map.get('id_ipv4') is not None:
                vip.ip = Ip().get_by_pk(vip_map.get('id_ipv4'))

            # Existing IPv6 ID
            if vip_map.get('id_ipv6') is not None:
                vip.ipv6 = Ipv6().get_by_pk(vip_map.get('id_ipv6'))

            # Host
            host_name = vip_map.get('host')
            if not is_valid_string_minsize(host_name, 3) or not is_valid_string_maxsize(host_name, 100):
                self.log.error(u'Host_name value is invalid: %s.', host_name)
                raise InvalidValueError(None, 'host_name', host_name)

            # Areanegocio
            areanegocio = vip_map.get('areanegocio')
            if not is_valid_string_minsize(areanegocio, 3) or not is_valid_string_maxsize(areanegocio, 100):
                self.log.error(
                    u'Areanegocio value is invalid: %s.', areanegocio)
                raise InvalidValueError(None, 'areanegocio', areanegocio)

            # Nome_servico
            nome_servico = vip_map.get('nome_servico')
            if not is_valid_string_minsize(nome_servico, 3) or not is_valid_string_maxsize(nome_servico, 100):
                self.log.error(
                    u'Nome_servico value is invalid: %s.', nome_servico)
                raise InvalidValueError(None, 'nome_servico', nome_servico)

            # Existing l7_filter
            if vip_map.get('l7_filter') is not None:
                vip.l7_filter = vip_map.get('l7_filter')

            # If the l7_filter is a rule
            if vip_map.get('rule_id') is not None:
                if not is_valid_int_greater_zero_param(vip_map.get('rule_id')):
                    self.log.error(
                        u'The rule_id parameter is not a valid value: %s.', vip_map.get('rule_id'))
                    raise InvalidValueError(
                        None, 'rule_id', vip_map.get('rule_id'))

                rule = Rule.objects.get(pk=vip_map.get('rule_id'))
                vip.l7_filter = '\n'.join(
                    rule.rulecontent_set.all().values_list('content', flat=True))
                vip.rule = rule

            environments = Ambiente.objects.filter(
                Q(vlan__networkipv4__ambient_vip=evip) |
                Q(vlan__networkipv6__ambient_vip=evip)
            )

            if pool_ids:

                try:

                    is_valid_list_int_greater_zero_param(pool_ids)

                except ValueError, error:
                    self.log.error(error)
                    raise InvalidValueError(
                        None,
                        'pool_ids',
                        pool_ids
                    )

                # Valid equipment by environment
                for pool_id in pool_ids:
                    serv_pool = ServerPool.objects.get(id=pool_id)
                    if serv_pool.environment not in environments:
                        raise IpNotFoundByEquipAndVipError(None, error_messages.get(373) % (serv_pool.id, evip.id))
            # set variables
            vip.filter_valid = 1
            vip.validado = 0
            vip.vip_criado = 0
            vip.set_variables(vip_map)

            try:
                # save Resquest Vip
                vip.save(user)

                for pool_id in pool_ids:

                    pool_obj = ServerPool.objects.get(id=pool_id)

                    vip_port_pool_obj = VipPortToPool(
                        requisicao_vip=vip,
                        server_pool=pool_obj,
                        port_vip=pool_obj.default_port
                    )

                    vip_port_pool_obj.save(user)

                # save VipPortToPool, ServerPool and ServerPoolMember
                # vip.save_vips_and_ports(vip_map, user)
            except Exception, e:
                if isinstance(e, IntegrityError):
                    # Duplicate value for Port Vip, Port Real and IP
                    self.log.error(u'Failed to save the request vip.')
                    return self.response_error(353)
                else:
                    raise e
#                    self.log.error(u'Failed to save the request vip.')
#                    raise RequisicaoVipsError(e, u'Failed to save the request vip')

            vip_map = dict()
            vip_map['id'] = vip.id

            return self.response(dumps_networkapi({'requisicao_vip': vip_map}))

        except ServerPool.DoesNotExist, e:
            self.log.error(str(e))
            return self.response_error(372)

        except IpNotFoundByEquipAndVipError, e:
            return self.response_error(334, e.message)
        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)
        except EnvironmentVipNotFoundError:
            return self.response_error(316, vip_map['finalidade'], vip_map['cliente'], vip_map['ambiente'])
        except IpNotFoundError:
            return self.response_error(119)
        except HealthcheckExpectNotFoundError:
            return self.response_error(124)
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
        except Rule.DoesNotExist:
            return self.response_error(358)
        except (RequisicaoVipsError, EquipamentoError, IpError, HealthcheckExpectError, GrupoError), e:
            return self.response_error(1)

    def handle_put(self, request, user, *args, **kwargs):
        """Treat requests PUT change request VIP.

        URLs: /requestvip/<id_vip>/
        """

        self.log.info("Change request VIP")

        try:

            vip_id = kwargs.get('id_vip')

            # Load XML data
            xml_map, attrs_map = loads(request.raw_post_data, ['pool_ids'])

            # XML data format
            networkapi_map = xml_map.get('networkapi')
            if networkapi_map is None:
                return self.response_error(3, u'There is no value to the networkapi tag  of XML request.')

            vip_map = networkapi_map.get('vip')
            if vip_map is None:
                return self.response_error(3, u'There is no value to the vip tag  of XML request.')

            # User permission
            if not has_perm(user, AdminPermission.VIP_ALTER_SCRIPT, AdminPermission.WRITE_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                raise UserNotAuthorizedError(None)

            # Valid Vip ID
            if not is_valid_int_greater_zero_param(vip_id):
                self.log.error(
                    u'The vip_id parameter is not a valid value: %s.', vip_id)
                raise InvalidValueError(None, 'vip_id', vip_id)

            # Valid Ipv4 and Ipv6 ID
            if (vip_map.get('id_ipv4') is None and vip_map.get('id_ipv6') is None):
                self.log.error(
                    u'The id_ipv4 and id_ipv6 parameter is not a valid value: %s.', vip_map.get('id_ipv4'))
                raise InvalidValueError(
                    None, 'id_ipv4 e id_vip6', vip_map.get('id_ipv4'))

            if (vip_map.get('id_ipv4') != None):
                if not is_valid_int_greater_zero_param(vip_map.get('id_ipv4')):
                    self.log.error(
                        u'The id_ipv4 parameter is not a valid value: %s.', vip_map.get('id_ipv4'))
                    raise InvalidValueError(
                        None, 'id_ipv4', vip_map.get('id_ipv4'))

            if (vip_map.get('id_ipv6') != None):
                if not is_valid_int_greater_zero_param(vip_map.get('id_ipv6')):
                    self.log.error(
                        u'The id_ipv6 parameter is not a valid value: %s.', vip_map.get('id_ipv6'))
                    raise InvalidValueError(
                        None, 'id_ipv6', vip_map.get('id_ipv6'))

            # Valid Vip validated
            if not is_valid_boolean_param(vip_map.get('validado')):
                self.log.error(
                    u'The validated parameter is not a valid value: %s.', vip_map.get('validado'))
                raise InvalidValueError(
                    None, 'validated', vip_map.get('validado'))

            # Valid Vip vip_created
            if not is_valid_boolean_param(vip_map.get('vip_criado')):
                self.log.error(
                    u'The vip_created parameter is not a valid value: %s.', vip_map.get('vip_criado'))
                raise InvalidValueError(
                    None, 'vip_created', vip_map.get('vip_criado'))

            pool_ids = vip_map.get('pool_ids', [])

            # Existing Vip ID
            vip = RequisicaoVips.get_by_pk(vip_id)

            with distributedlock(LOCK_VIP % vip_id):

                # Valid Vip created
                if vip.vip_criado:
                    self.log.error(
                        u'The IP of the request for VIP %d can not be changed because the VIP is already created.' % vip.id)
                    raise RequisicaoVipsAlreadyCreatedError(None)

                # Get variables
                variables_map = vip.variables_to_map()

                # Valid variables
                vip.set_variables(variables_map)

                evip = EnvironmentVip.get_by_values(
                    variables_map.get('finalidade'),
                    variables_map.get('cliente'),
                    variables_map.get('ambiente')
                )

                # Existing IPv4 ID
                if vip_map.get('id_ipv4') is not None:
                    vip.ip = Ip().get_by_pk(vip_map.get('id_ipv4'))
                else:
                    vip.ip = None

                # Existing IPv6 ID
                if vip_map.get('id_ipv6') is not None:
                    vip.ipv6 = Ipv6().get_by_pk(vip_map.get('id_ipv6'))
                else:
                    vip.ipv6 = None

                # Existing l7_filter
                if vip_map.get('l7_filter') is not None:
                    vip.l7_filter = vip_map.get('l7_filter')
                else:
                    vip.l7_filter = None

                # If the l7_filter is a rule, set filter_valid to TRUE
                if vip_map.get('rule_id') is not None:
                    # Valid rule
                    if not is_valid_int_greater_zero_param(vip_map.get('rule_id')):
                        self.log.error(
                            u'The rule_id parameter is not a valid value: %s.', vip_map.get('rule_id'))
                        raise InvalidValueError(
                            None, 'rule_id', vip_map.get('rule_id'))

                    rule = Rule.objects.get(pk=vip_map.get('rule_id'))
                    vip.l7_filter = '\n'.join(
                        rule.rulecontent_set.all().values_list('content', flat=True))
                    vip.rule = rule
                else:
                    vip.rule = None

                if pool_ids:
                    try:

                        is_valid_list_int_greater_zero_param(pool_ids)

                    except ValueError, error:
                        self.log.error(error)
                        raise InvalidValueError(
                            None,
                            'pool_ids',
                            pool_ids
                        )

                # set variables
                vip.filter_valid = 1
                vip.validado = 0
                vip.set_variables(vip_map)

                try:
                    # update Resquest Vip
                    vip.save(user)

                    # Remove VipPortPool Related
                    for vip_port_pool in vip.vipporttopool_set.all():
                        vip_port_pool.delete(user)

                    # Related Pool with Vip
                    for pool_id in pool_ids:

                        pool_obj = ServerPool.objects.get(id=pool_id)

                        vip_port_pool_obj = VipPortToPool(
                            requisicao_vip=vip,
                            server_pool=pool_obj,
                            port_vip=pool_obj.default_port
                        )

                        vip_port_pool_obj.save(user)

                except Exception, e:
                    if isinstance(e, IntegrityError):
                        # Duplicate value for Port Vip, Port Real and IP
                        self.log.error(u'Failed to update the request vip.')
                        return self.response_error(353)
                    else:
                        self.log.error(u'Failed to update the request vip.')
                        raise RequisicaoVipsError(
                            e, u'Failed to update the request vip')

                return self.response(dumps_networkapi({}))

        except ServerPool.DoesNotExist, e:
            return self.response_error(372)

        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)
        except EnvironmentVipNotFoundError:
            return self.response_error(316, vip_map['finalidade'], vip_map['cliente'], vip_map['ambiente'])
        except RequisicaoVipsAlreadyCreatedError:
            return self.response_error(186, vip_id)
        except IpNotFoundError:
            return self.response_error(119)
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
        except Rule.DoesNotExist:
            return self.response_error(358)
        except (RequisicaoVipsError, EquipamentoError, IpError, HealthcheckExpectError, GrupoError), e:
            return self.response_error(1)
