# -*- coding:utf-8 -*-
'''
Title: Infrastructure NetworkAPI
Author: avanzolin / S2IT
Copyright: ( c )  2009 globo.com todos os direitos reservados.
'''
from __future__ import with_statement
from networkapi.admin_permission import AdminPermission
from networkapi.auth import has_perm
from networkapi.distributedlock import distributedlock, LOCK_VIP
from networkapi.equipamento.models import EquipamentoNotFoundError, EquipamentoError, Equipamento
from networkapi.exception import InvalidValueError, RequestVipsNotBeenCreatedError, EquipmentGroupsNotAuthorizedError
from networkapi.grupo.models import GrupoError
from networkapi.healthcheckexpect.models import HealthcheckExpect, HealthcheckExpectNotFoundError, HealthcheckExpectError
from networkapi.infrastructure.script_utils import exec_script, ScriptError
from networkapi.infrastructure.xml_utils import loads, dumps_networkapi, XMLError
from networkapi.ip.models import IpNotFoundError, IpEquipmentNotFoundError, IpError, IpNotFoundByEquipAndVipError
from networkapi.log import Log
from networkapi.requisicaovips.models import RequisicaoVips, RequisicaoVipsNotFoundError, RequisicaoVipsError, \
    InvalidFinalidadeValueError, InvalidMetodoBalValueError, InvalidPersistenciaValueError, \
    InvalidClienteValueError, InvalidAmbienteValueError, InvalidCacheValueError, \
    InvalidHealthcheckTypeValueError, InvalidHealthcheckValueError, \
    InvalidTimeoutValueError, InvalidHostNameError, InvalidMaxConValueError, \
    InvalidServicePortValueError, InvalidRealValueError, InvalidBalAtivoValueError, \
    InvalidTransbordoValueError, InvalidPriorityValueError
from networkapi.rest import RestResource, UserNotAuthorizedError
from networkapi.util import is_valid_int_greater_zero_param, clone
from string import upper
from networkapi.ambiente.models import EnvironmentVip


class RequestHealthcheckResource(RestResource):

    log = Log('RequestHealthcheckResource')

    def handle_put(self, request, user, *args, **kwargs):
        """
        Handles PUT requests to change the VIP's healthcheck.

        URL: vip/<id_vip>/healthcheck
        """

        self.log.info("Change VIP's healthcheck")

        try:

            # Commons Validations

            # User permission
            if not has_perm(
                    user,
                    AdminPermission.VIP_ALTER_SCRIPT,
                    AdminPermission.WRITE_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                raise UserNotAuthorizedError(None)

            # Valid Vip ID
            vip_id = kwargs.get('id_vip')
            if not is_valid_int_greater_zero_param(vip_id):
                self.log.error(
                    u'The vip_id parameter is not a valid value: %s.',
                    vip_id)
                raise InvalidValueError(None)

            # Existing Vip ID
            vip = RequisicaoVips.get_by_pk(vip_id)

            with distributedlock(LOCK_VIP % vip_id):

                vip_old = clone(vip)

                # Vip must be created
                if not vip.vip_criado:
                    self.log.error(
                        u'Healthcheck can not be changed because VIP has not yet been created.')
                    raise RequestVipsNotBeenCreatedError(None)

                # Vip equipments permission
                if vip.ip is not None:
                    for ip_equipment in vip.ip.ipequipamento_set.all():
                        if not has_perm(
                                user,
                                AdminPermission.VIP_ALTER_SCRIPT,
                                AdminPermission.WRITE_OPERATION,
                                None,
                                ip_equipment.equipamento_id,
                                AdminPermission.EQUIP_UPDATE_CONFIG_OPERATION):
                            self.log.error(
                                u'Groups of equipment registered with the IP of the  VIP request  is not allowed of acess.')
                            raise EquipmentGroupsNotAuthorizedError(None)

                if vip.ipv6 is not None:
                    for ip_equipment in vip.ipv6.ipv6equipament_set.all():
                        if not has_perm(
                                user,
                                AdminPermission.VIP_ALTER_SCRIPT,
                                AdminPermission.WRITE_OPERATION,
                                None,
                                ip_equipment.equipamento_id,
                                AdminPermission.EQUIP_UPDATE_CONFIG_OPERATION):
                            self.log.error(
                                u'Groups of equipment registered with the IP of the  VIP request  is not allowed of acess.')
                            raise EquipmentGroupsNotAuthorizedError(None)

                # Business Validations

                # Load XML data
                xml_map, attrs_map = loads(request.raw_post_data)

                # XML data format
                networkapi_map = xml_map.get('networkapi')
                if networkapi_map is None:
                    return self.response_error(
                        3,
                        u'There is no value to the networkapi tag of XML request.')
                vip_map = networkapi_map.get('vip')
                if vip_map is None:
                    return self.response_error(
                        3,
                        u'There is no value to the vip tag of XML request.')

                # Get XML data
                healthcheck_type = upper(str(vip_map['healthcheck_type']))
                healthcheck = vip_map['healthcheck']
                id_healthcheck_expect = vip_map['id_healthcheck_expect']

                vars = vip.variables_to_map()
                environment_vip = EnvironmentVip.get_by_values(
                    vars.get('finalidade'),
                    vars.get('cliente'),
                    vars.get('ambiente'))

                healthcheck_is_valid = RequisicaoVips.heathcheck_exist(
                    healthcheck_type,
                    environment_vip.id)

                # healthcheck_type exist'
                if not healthcheck_is_valid:
                    self.log.error(
                        u'The healthcheck_type parameter not exist.')
                    raise InvalidValueError(
                        u'The healthcheck_type parameter not exist.',
                        'healthcheck_type',
                        healthcheck_type)

                # If healthcheck_type is not HTTP id_healthcheck_expect and
                # healthcheck must be None
                if healthcheck_type != 'HTTP':
                    if not (
                            id_healthcheck_expect is None and healthcheck is None):
                        msg = u'The healthcheck_type parameter is %s, then healthcheck and id_healthcheck_expect must be None.' % healthcheck_type
                        self.log.error(msg)
                        raise InvalidValueError(msg)
#                         return self.response_error(276)
                # If healthcheck_type is 'HTTP' id_healthcheck_expect and
                # healthcheck must NOT be None
                elif healthcheck_type == 'HTTP':
                    if id_healthcheck_expect is None or healthcheck is None:
                        msg = u'The healthcheck_type parameter is HTTP, then healthcheck and id_healthcheck_expect must NOT be None.'
                        self.log.error(msg)
                        raise InvalidValueError(msg)
                    else:
                        try:

                            # Valid healthcheck_expect ID
                            if not is_valid_int_greater_zero_param(
                                    id_healthcheck_expect):
                                self.log.error(
                                    u'The id_healthcheck_expect parameter is not a valid value: %s.',
                                    id_healthcheck_expect)
                                raise InvalidValueError(
                                    None,
                                    'id_healthcheck_expect',
                                    id_healthcheck_expect)

                            # Find healthcheck_expect by ID to check if it
                            # exist
                            healthcheck_expect = HealthcheckExpect.get_by_pk(
                                id_healthcheck_expect)

                            # Check if healthcheck is a string
                            if not isinstance(healthcheck, basestring):
                                msg = u'The healthcheck must be a string.'
                                self.log.error(msg)
                                raise InvalidValueError(
                                    msg,
                                    'healthcheck',
                                    healthcheck)

                        except HealthcheckExpectNotFoundError:
                            msg = u'The id_healthcheck_expect parameter does not exist.'
                            self.log.error(msg)
                            raise InvalidValueError(
                                msg,
                                'id_healthcheck_expect',
                                id_healthcheck_expect)

                # Business Rules

                # Get variables
                variables_map = vip.variables_to_map()

                # Valid variables
                vip.set_variables(variables_map)

                # Set healthcheck_type
                variables_map['healthcheck_type'] = healthcheck_type

                # If healthcheck_type is HTTP
                if healthcheck_type == 'HTTP':
                    # Set healthcheck
                    variables_map['healthcheck'] = healthcheck

                    # Set id_healthcheck_expect
                    vip.healthcheck_expect = healthcheck_expect
                else:
                    # Set healthcheck to None
                    variables_map['healthcheck'] = None

                    # Set id_healthcheck_expect to None
                    vip.healthcheck_expect = None

                # Set variables
                vip.set_variables(variables_map)

                # Save VIP
                vip.save(user, commit=True)

                # Executar script

                # gerador_vips -i <ID_REQUISICAO> --healthcheck
                command = 'gerador_vips -i %d --healthcheck' % vip.id
                code, stdout, stderr = exec_script(command)

                if code == 0:
                    success_map = dict()
                    success_map['codigo'] = '%04d' % code
                    success_map['descricao'] = {
                        'stdout': stdout,
                        'stderr': stderr}

                    map = dict()
                    map['sucesso'] = success_map
                    return self.response(dumps_networkapi(map))
                else:
                    vip_old.save(user, commit=True)
                    return self.response_error(2, stdout + stderr)

        except XMLError as x:
            self.log.error(u'Error reading the XML request.')
            return self.response_error(3, x)
        except ScriptError as s:
            return self.response_error(2, s)
        except EquipmentGroupsNotAuthorizedError:
            return self.response_error(271)
        except RequestVipsNotBeenCreatedError:
            return self.response_error(270, vip_id)
        except InvalidValueError as e:
            return self.response_error(332, e.param, e.value)
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
        except InvalidHealthcheckValueError:
            return self.response_error(134)
        except InvalidTimeoutValueError:
            return self.response_error(135)
        except InvalidHostNameError:
            return self.response_error(136)
        except InvalidMaxConValueError:
            return self.response_error(137)
        except InvalidServicePortValueError as e:
            porta = 'nulo'
            if e.message is not None:
                porta = e.message
            return self.response_error(138, porta)
        except InvalidRealValueError as e:
            real = 'nulo'
            if e.message is not None:
                real = e.message
            return self.response_error(151, real)
        except InvalidBalAtivoValueError:
            return self.response_error(129)
        except InvalidTransbordoValueError as e:
            transbordo = 'nulo'
            if e.message is not None:
                transbordo = e.message
            return self.response_error(130, transbordo)
        except UserNotAuthorizedError:
            return self.not_authorized()
        except IpNotFoundByEquipAndVipError:
            return self.response_error(334, e.message)
        except (RequisicaoVipsError, EquipamentoError, IpError, HealthcheckExpectError, GrupoError) as e:
            return self.response_error(1)
