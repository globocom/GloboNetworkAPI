# -*- coding:utf-8 -*-
'''
Title: Infrastructure NetworkAPI
Author: avanzolin / TQI
Copyright: ( c )  2009 globo.com todos os direitos reservados.
'''
from django.conf import settings
from networkapi.admin_permission import AdminPermission
from networkapi.ambiente.models import Ambiente, AmbienteNotFoundError, AmbienteError
from networkapi.auth import has_perm
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.log import Log
from networkapi.rest import RestResource, UserNotAuthorizedError
from networkapi.util import is_valid_int_greater_zero_param
from networkapi.exception import InvalidValueError
from django.forms.models import model_to_dict


class VlanGetByEnvironmentResource(RestResource):

    log = Log('VlanGetByEnvironmentResource')

    def handle_get(self, request, user, *args, **kwargs):
        """Handle GET requests to get VLAN by environment.

        URLs: /vlan/ambiente/<id_ambiente>/,
        """
        try:
            id_env = kwargs.get('id_ambiente')

            # User permission
            if not has_perm(
                    user,
                    AdminPermission.VLAN_MANAGEMENT,
                    AdminPermission.READ_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                raise UserNotAuthorizedError(None)

            # Valid Vlan ID
            if not is_valid_int_greater_zero_param(id_env):
                self.log.error(
                    u'The id_env parameter is not a valid value: %s.',
                    id_env)
                raise InvalidValueError(None, 'env_id', id_env)

            environment = Ambiente().get_by_pk(id_env)
            """vlans = client.create_vlan().get(id_vlan)
            
            vlans = vlans.get('vlan')
            
            redesIPV4 = vlans["redeipv4"]"""
            map_list = []

            for vlan in environment.vlan_set.all():
                rede_ipv4 = vlan.networkipv4_set.all()
                dict_vlan = model_to_dict(vlan)

                if rede_ipv4:
                    rede_ipv4 = rede_ipv4[0]
                    rede_ipv4 = model_to_dict(rede_ipv4)
                    dict_vlan['id_tipo_rede'] = rede_ipv4['network_type']
                    dict_vlan['rede_oct1'] = rede_ipv4['oct1']
                    dict_vlan['rede_oct2'] = rede_ipv4['oct2']
                    dict_vlan['rede_oct3'] = rede_ipv4['oct3']
                    dict_vlan['rede_oct4'] = rede_ipv4['oct4']
                    dict_vlan['bloco'] = rede_ipv4['block']
                    dict_vlan['mascara_oct1'] = rede_ipv4['mask_oct1']
                    dict_vlan['mascara_oct2'] = rede_ipv4['mask_oct2']
                    dict_vlan['mascara_oct3'] = rede_ipv4['mask_oct3']
                    dict_vlan['mascara_oct4'] = rede_ipv4['mask_oct4']
                    dict_vlan['broadcast'] = rede_ipv4['broadcast']
                else:
                    dict_vlan['id_tipo_rede'] = ''
                    dict_vlan['rede_oct1'] = ''
                    dict_vlan['rede_oct2'] = ''
                    dict_vlan['rede_oct3'] = ''
                    dict_vlan['rede_oct4'] = ''
                    dict_vlan['bloco'] = ''
                    dict_vlan['mascara_oct1'] = ''
                    dict_vlan['mascara_oct2'] = ''
                    dict_vlan['mascara_oct3'] = ''
                    dict_vlan['mascara_oct4'] = ''
                    dict_vlan['broadcast'] = ''

                map_list.append(dict_vlan)

            return self.response(dumps_networkapi({'vlan': map_list}))

        except InvalidValueError as e:
            return self.response_error(269, e.param, e.value)

        except UserNotAuthorizedError:
            return self.not_authorized()

        except AmbienteNotFoundError:
            return self.response_error(112)
        except AmbienteError:
            return self.response_error(1)
