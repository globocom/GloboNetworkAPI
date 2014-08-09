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
from networkapi.ip.models import Ipv6, IpNotFoundError, IpError, IpEquipmentNotFoundError, Ipv6Equipament
from networkapi.equipamento.models import Equipamento, EquipamentoNotFoundError, EquipamentoError


class IPv6GetResource(RestResource):

    log = Log('IPv6GetResource')

    def handle_get(self, request, user, *args, **kwargs):
        """Handles GET requests to get a ipv6.

        URLs: ipv6/get/id_ip6
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
            id_ip = kwargs.get('id_ipv6')

            if not is_valid_int_greater_zero_param(id_ip):
                raise InvalidValueError(None, 'id_ip', id_ip)

            # Business Rules

            ip = Ipv6()

            ip = ip.get_by_pk(id_ip)

            EquipIps = []
            mapa = dict()
            #lista = []

            try:

                EquipIps = []
                equipsIp = Ipv6Equipament.list_by_ip6(ip.id)
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
            ip_maps['block1'] = ip.block1
            ip_maps['block2'] = ip.block2
            ip_maps['block3'] = ip.block3
            ip_maps['block4'] = ip.block4
            ip_maps['block5'] = ip.block5
            ip_maps['block6'] = ip.block6
            ip_maps['block7'] = ip.block7
            ip_maps['block8'] = ip.block8
            ip_maps['descricao'] = ip.description
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
        except EquipamentoNotFoundError as e:
            return self.response_error(281, id_ip)
        except EquipamentoError as e:
            return self.response_error(1)
        except IpEquipmentNotFoundError as e:
            return self.response_error(281, id_ip)
        except (IpError):
            return self.response_error(1)
        except XMLError as x:
            self.log.error(u'Error reading the XML request.')
            return self.response_error(3, x)
