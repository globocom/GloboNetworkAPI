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
from networkapi.ip.models import Ip, IpNotFoundError, IpError, IpEquipmentNotFoundError, IpEquipamento, NetworkIPv4, NetworkIPv4NotFoundError
from networkapi.equipamento.models import Equipamento, EquipamentoNotFoundError, EquipamentoError


class IPv4ListResource(RestResource):

    log = Log('NetworkIPv4GetResource')

    def handle_get(self, request, user, *args, **kwargs):
        """Handles GET requests to list all network IPv4 by network ipv4 id.

        URLs: ip/id_network_ipv4/id_rede 
        """

        try:

            # Commons Validations

            # User permission
            if not has_perm(user, AdminPermission.IPS, AdminPermission.READ_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                return self.not_authorized()

            # Business Validations

            # Valid id access
            id_network = kwargs.get('id_rede')

            if not is_valid_int_greater_zero_param(id_network):
                raise InvalidValueError(None, 'id_rede', id_network)

            # Business Rules

            NetworkIPv4.get_by_pk(id_network)

            ips = Ip.list_by_network(id_network)

            try:
                len(ips)
            except Exception, e:
                raise InvalidValueError(None, 'id_rede', id_network)

            if ips == None or len(ips) <= 0:
                raise IpNotFoundError(305, id_network)

            EquipIps = []
            mapa = dict()
            #lista = []

            try:
                for ip in ips:
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

            for ip in ips:
                lequips = []
                ip_maps = dict()
                ip_maps = model_to_dict(ip)

                for equip in mapa.get(ip.id):
                    equip = Equipamento.get_by_pk(equip.equipamento.id)
                    lequips.append(model_to_dict(equip))

                ip_maps['equipamento'] = lequips
                list_ips.append(ip_maps)

            network_map['ips'] = list_ips

            # Return XML
            return self.response(dumps_networkapi(network_map))

        except InvalidValueError, e:
            self.log.error(
                u'Parameter %s is invalid. Value: %s.', e.param, e.value)
            return self.response_error(269, e.param, e.value)
        except (NetworkIPv4NotFoundError, EquipamentoNotFoundError, IpEquipmentNotFoundError):
            return self.response_error(281)
        except IpNotFoundError:
            return self.response_error(305, id_network)
        except (IpError, EquipamentoError):
            return self.response_error(1)
        except XMLError, x:
            self.log.error(u'Error reading the XML request.')
            return self.response_error(3, x)
