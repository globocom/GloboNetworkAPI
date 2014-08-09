# -*- coding:utf-8 -*-
'''
Title: Infrastructure NetworkAPI
Author: avanzolin / TQI
Copyright: ( c )  2009 globo.com todos os direitos reservados.
'''
from __future__ import with_statement
from networkapi.admin_permission import AdminPermission
from networkapi.auth import has_perm
from networkapi.grupo.models import GrupoError
from networkapi.infrastructure.xml_utils import loads, XMLError, dumps_networkapi
from networkapi.ip.models import IpError
from networkapi.log import Log
from networkapi.rest import RestResource
from networkapi.util import is_valid_int_greater_zero_param
from networkapi.exception import InvalidValueError
from networkapi.equipamento.models import EquipamentoError, EquipamentoNotFoundError
from networkapi.settings import VIP_REMOVE
from networkapi.infrastructure.script_utils import exec_script, ScriptError
from networkapi.requisicaovips.models import RequisicaoVipsNotFoundError, RequisicaoVipsError, RequisicaoVips
from networkapi.healthcheckexpect.models import HealthcheckExpectError
from networkapi.distributedlock import distributedlock, LOCK_VIP


class RemoveVipResource(RestResource):

    log = Log('RemoveVipResource')

    def handle_post(self, request, user, *args, **kwargs):
        '''Treat POST requests to run remove script for vip

        URL: vip/remove/
        '''

        try:

            # Commons Validations

            # User permission
            if not has_perm(
                    user,
                    AdminPermission.VIP_REMOVE_SCRIPT,
                    AdminPermission.WRITE_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                return self.not_authorized()

            # Business Validations

            # Load XML data
            xml_map, attrs_map = loads(request.raw_post_data)

            # XML data format
            networkapi_map = xml_map.get('networkapi')
            if networkapi_map is None:
                msg = u'There is no value to the networkapi tag of XML request.'
                self.log.error(msg)
                return self.response_error(3, msg)
            vip_map = networkapi_map.get('vip')
            if vip_map is None:
                msg = u'There is no value to the vlan tag of XML request.'
                self.log.error(msg)
                return self.response_error(3, msg)

            # Get XML data
            vip_id = vip_map.get('id_vip')

            # Valid vip ID
            if not is_valid_int_greater_zero_param(vip_id):
                self.log.error(
                    u'Parameter id_vip is invalid. Value: %s.',
                    vip_id)
                raise InvalidValueError(None, 'id_vip', vip_id)

            # Vip must exists in database
            vip = RequisicaoVips.get_by_pk(vip_id)

            with distributedlock(LOCK_VIP % vip_id):

                # Equipment permissions
                if vip.ip is not None:
                    for ip_equipment in vip.ip.ipequipamento_set.all():
                        if not has_perm(
                                user,
                                AdminPermission.VIP_CREATE_SCRIPT,
                                AdminPermission.WRITE_OPERATION,
                                None,
                                ip_equipment.equipamento_id,
                                AdminPermission.EQUIP_UPDATE_CONFIG_OPERATION):
                            return self.not_authorized()

                if vip.ipv6 is not None:
                    for ip_equipment in vip.ipv6.ipv6equipament_set.all():
                        if not has_perm(
                                user,
                                AdminPermission.VIP_CREATE_SCRIPT,
                                AdminPermission.WRITE_OPERATION,
                                None,
                                ip_equipment.equipamento_id,
                                AdminPermission.EQUIP_UPDATE_CONFIG_OPERATION):
                            return self.not_authorized()

                # Must be validated
                if not vip.validado:
                    return self.response_error(191, vip_id)

                # Must be created
                if not vip.vip_criado:
                    return self.response_error(322, vip_id)

                # Business Rules

                # Make command
                command = VIP_REMOVE % (vip.id)

                # Execute command
                code, stdout, stderr = exec_script(command)
                if code == 0:

                    success_map = dict()
                    success_map['codigo'] = '%04d' % code
                    success_map['descricao'] = {
                        'stdout': stdout,
                        'stderr': stderr}

                    vip.vip_criado = 0
                    vip.save(user)

                    map = dict()
                    map['sucesso'] = success_map

                else:
                    return self.response_error(2, stdout + stderr)

                # Return XML
                return self.response(dumps_networkapi(map))

        except InvalidValueError as e:
            return self.response_error(269, e.param, e.value)
        except EquipamentoNotFoundError as e:
            return self.response_error(117)
        except RequisicaoVipsNotFoundError as e:
            return self.response_error(152)
        except XMLError as e:
            self.log.error(u'Error reading the XML request.')
            return self.response_error(3, e)
        except ScriptError as s:
            return self.response_error(2, s)
        except (RequisicaoVipsError, GrupoError, HealthcheckExpectError, EquipamentoError, IpError):
            return self.response_error(1)
