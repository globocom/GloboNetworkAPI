# -*- coding:utf-8 -*-
'''
Title: Infrastructure NetworkAPI
Author: globo.com / TQI
Copyright: ( c )  2009 globo.com todos os direitos reservados.
'''

from networkapi.rest import RestResource
from networkapi.auth import has_perm
from networkapi.admin_permission import AdminPermission
from networkapi.infrastructure.xml_utils import XMLError, dumps_networkapi
from networkapi.log import Log
from networkapi.exception import InvalidValueError
from networkapi.util import is_valid_int_greater_zero_param
from django.forms.models import model_to_dict
from networkapi.ip.models import Ip, IpNotFoundError, IpError, IpEquipmentNotFoundError, IpEquipamento
from networkapi.equipamento.models import Equipamento, EquipamentoNotFoundError, EquipamentoError


class IPv4GetResource(RestResource):

    log = Log('IPv4GetResource')

    def handle_get(self, request, user, *args, **kwargs):
        """Handles GET requests to get a ipv4.

        URLs: ip/get/id_ip
        """

        try:
            # Commons Validations

            # User permission
            if not has_perm(
                    user,
                    AdminPermission.IPS,
                    AdminPermission.READ_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                return self.not_authorized()

            # Business Validations

            # Valid id access
            id_ip = kwargs.get('id_ip')

            if not is_valid_int_greater_zero_param(id_ip):
                raise InvalidValueError(None, 'id_ip', id_ip)

            # Business Rules

            ip = Ip()

            ip = ip.get_by_pk(id_ip)

            EquipIps = []
            mapa = dict()
            #lista = []

            try:

                EquipIps = []
                equipsIp = IpEquipamento.list_by_ip(ip.id)
                for eIp in equipsIp:
                    EquipIps.append(eIp)
                mapa[ip.id] = EquipIps
                # lista.append(mapa)

            except IpEquipmentNotFoundError:
                EquipIps.append(None)
            except IpError:
                EquipIps.append(None)

            network_map = dict()

            list_ips = []
            lequips = []

            lequips = []
            ip_maps = dict()
            ip_maps['id'] = ip.id
            ip_maps['oct1'] = ip.oct1
            ip_maps['oct2'] = ip.oct2
            ip_maps['oct3'] = ip.oct3
            ip_maps['oct4'] = ip.oct4
            ip_maps['descricao'] = ip.descricao
            for equip in mapa.get(ip.id):
                equip = Equipamento.get_by_pk(equip.equipamento.id)
                lequips.append(model_to_dict(equip))
            ip_maps['equipamento'] = lequips
            list_ips.append(ip_maps)

            list_ips

            network_map['ips'] = list_ips

            # Return XML
            return self.response(dumps_networkapi(network_map))

        except InvalidValueError as e:
            self.log.error(
                u'Parameter %s is invalid. Value: %s.',
                e.param,
                e.value)
            return self.response_error(269, e.param, e.value)
        except IpNotFoundError as e:
            return self.response_error(119)
        except (EquipamentoNotFoundError, IpEquipmentNotFoundError):
            return self.response_error(281, id_ip)
        except (IpError, EquipamentoError):
            return self.response_error(1)
        except XMLError as x:
            self.log.error(u'Error reading the XML request.')
            return self.response_error(3, x)
