# -*- coding:utf-8 -*-
'''
Title: Infrastructure NetworkAPI
Author: avanzolin / TQI
Copyright: ( c )  2009 globo.com todos os direitos reservados.
'''

from networkapi.admin_permission import AdminPermission
from networkapi.ambiente.models import EnvironmentVip
from networkapi.auth import has_perm
from networkapi.equipamento.models import EquipamentoNotFoundError, EquipamentoError, Equipamento
from networkapi.exception import InvalidValueError, EnvironmentVipNotFoundError
from networkapi.grupo.models import GrupoError
from networkapi.infrastructure.xml_utils import loads, XMLError, dumps_networkapi
from networkapi.ip.models import NetworkIPv4NotFoundError, IpError, NetworkIPv4Error, IpNotFoundByEquipAndVipError
from networkapi.log import Log
from networkapi.rest import RestResource, UserNotAuthorizedError
from networkapi.util import is_valid_int_greater_zero_param, is_valid_string_maxsize, is_valid_string_minsize, is_valid_regex


class IPEquipEvipResource(RestResource):

    log = Log('IPEquipEvipResource')

    def handle_post(self, request, user, *args, **kwargs):
        '''Handles POST requests to get all Ips (v4) or (v6) of equip on Divisao DC and Ambiente Logico of fisrt Network4 and 6 (if exists) of Environment Vip.

        URL: ip/getbyequipandevip/
        '''

        self.log.info('Get Ips by Equip - Evip')
        try:

            # User permission
            if not has_perm(user, AdminPermission.IPS, AdminPermission.READ_OPERATION):
                raise UserNotAuthorizedError(
                    None, u'User does not have permission to perform the operation.')

            # Load XML data
            xml_map, attrs_map = loads(request.raw_post_data)

            # XML data format
            networkapi_map = xml_map.get('networkapi')
            if networkapi_map is None:
                msg = u'There is no value to the networkapi tag of XML request.'
                self.log.error(msg)
                return self.response_error(3, msg)
            ip_map = networkapi_map.get('ip_map')
            if ip_map is None:
                msg = u'There is no value to the ip tag of XML request.'
                self.log.error(msg)
                return self.response_error(3, msg)

            # Get XML data
            id_evip = ip_map.get('id_evip')
            equip_name = ip_map.get('equip_name')

            # Valid id_evip
            if not is_valid_int_greater_zero_param(id_evip):
                self.log.error(
                    u'Parameter id_evip is invalid. Value: %s.', id_evip)
                raise InvalidValueError(None, 'id_evip', id_evip)

            # Valid equip_name
            if not is_valid_string_minsize(equip_name, 3) or not is_valid_string_maxsize(equip_name, 80) or not is_valid_regex(equip_name, "^[A-Z0-9-_]+$"):
                self.log.error(
                    u'Parameter equip_name is invalid. Value: %s', equip_name)
                raise InvalidValueError(None, 'equip_name', equip_name)

            # Business Rules

            # Get Environment VIp
            evip = EnvironmentVip.get_by_pk(id_evip)
            # Get Equipment
            equip = Equipamento.get_by_name(equip_name)

            lista_ips_equip = list()
            lista_ipsv6_equip = list()

            # GET DIVISAO DC AND AMBIENTE_LOGICO OF NET4 AND NET6
            lista_amb_div_4 = list()
            lista_amb_div_6 = list()
            for net in evip.networkipv4_set.select_related().all():

                dict_div_4 = dict()
                dict_div_4['divisao_dc'] = net.vlan.ambiente.divisao_dc_id
                dict_div_4[
                    'ambiente_logico'] = net.vlan.ambiente.ambiente_logico_id

                if dict_div_4 not in lista_amb_div_4:
                    lista_amb_div_4.append(dict_div_4)

            for net in evip.networkipv6_set.select_related().all():

                dict_div_6 = dict()
                dict_div_6['divisao_dc'] = net.vlan.ambiente.divisao_dc_id
                dict_div_6[
                    'ambiente_logico'] = net.vlan.ambiente.ambiente_logico_id
                if dict_div_6 not in lista_amb_div_6:
                    lista_amb_div_6.append(dict_div_6)

            # Get all IPV4's Equipment
            for ipequip in equip.ipequipamento_set.select_related().all():
                if ipequip.ip not in lista_ips_equip:
                    for dict_div_amb in lista_amb_div_4:
                        # if ipequip.ip.networkipv4.ambient_vip is not None and
                        # ipequip.ip.networkipv4.ambient_vip.id  == evip.id:
                        if (ipequip.ip.networkipv4.vlan.ambiente.divisao_dc.id == dict_div_amb.get('divisao_dc') and ipequip.ip.networkipv4.vlan.ambiente.ambiente_logico.id == dict_div_amb.get('ambiente_logico')):
                            lista_ips_equip.append(ipequip.ip)

            # Get all IPV6'S Equipment
            for ipequip in equip.ipv6equipament_set.select_related().all():
                if ipequip.ip not in lista_ipsv6_equip:
                    for dict_div_amb in lista_amb_div_6:
                        # if ipequip.ip.networkipv6.ambient_vip is not None and
                        # ipequip.ip.networkipv6.ambient_vip.id  == evip.id:
                        print ipequip.ip.networkipv6.vlan.ambiente.divisao_dc.id
                        print dict_div_amb.get('divisao_dc')
                        if (ipequip.ip.networkipv6.vlan.ambiente.divisao_dc.id == dict_div_amb.get('divisao_dc') and ipequip.ip.networkipv6.vlan.ambiente.ambiente_logico.id == dict_div_amb.get('ambiente_logico')):
                            lista_ipsv6_equip.append(ipequip.ip)

            # lists and dicts for return
            lista_ip_entregue = list()
            lista_ip6_entregue = list()

            for ip in lista_ips_equip:
                dict_ips4 = dict()
                dict_network = dict()

                dict_ips4['id'] = ip.id
                dict_ips4['ip'] = "%s.%s.%s.%s" % (
                    ip.oct1, ip.oct2, ip.oct3, ip.oct4)

                dict_network['id'] = ip.networkipv4_id
                dict_network["network"] = "%s.%s.%s.%s" % (
                    ip.networkipv4.oct1, ip.networkipv4.oct2, ip.networkipv4.oct3, ip.networkipv4.oct4)
                dict_network["mask"] = "%s.%s.%s.%s" % (
                    ip.networkipv4.mask_oct1, ip.networkipv4.mask_oct2, ip.networkipv4.mask_oct3, ip.networkipv4.mask_oct4)

                dict_ips4['network'] = dict_network

                lista_ip_entregue.append(dict_ips4)

            for ip in lista_ipsv6_equip:
                dict_ips6 = dict()
                dict_network = dict()

                dict_ips6['id'] = ip.id
                dict_ips6['ip'] = "%s:%s:%s:%s:%s:%s:%s:%s" % (
                    ip.block1, ip.block2, ip.block3, ip.block4, ip.block5, ip.block6, ip.block7, ip.block8)

                dict_network['id'] = ip.networkipv6.id
                dict_network["network"] = "%s:%s:%s:%s:%s:%s:%s:%s" % (
                    ip.networkipv6.block1, ip.networkipv6.block2, ip.networkipv6.block3, ip.networkipv6.block4, ip.networkipv6.block5, ip.networkipv6.block6, ip.networkipv6.block7, ip.networkipv6.block8)
                dict_network["mask"] = "%s:%s:%s:%s:%s:%s:%s:%s" % (
                    ip.networkipv6.block1, ip.networkipv6.block2, ip.networkipv6.block3, ip.networkipv6.block4, ip.networkipv6.block5, ip.networkipv6.block6, ip.networkipv6.block7, ip.networkipv6.block8)

                dict_ips6['network'] = dict_network

                lista_ip6_entregue.append(dict_ips6)

            lista_ip_entregue = lista_ip_entregue if len(
                lista_ip_entregue) > 0 else None
            lista_ip6_entregue = lista_ip6_entregue if len(
                lista_ip6_entregue) > 0 else None

            if (lista_ip_entregue is None and lista_ip6_entregue is None):
                raise IpNotFoundByEquipAndVipError(
                    None, 'Ip não encontrado com equipamento %s e ambiente vip %s' % (equip_name, id_evip))

            return self.response(dumps_networkapi({"ipv4": lista_ip_entregue, "ipv6": lista_ip6_entregue}))

        except IpNotFoundByEquipAndVipError:
            return self.response_error(317, equip_name, id_evip)
        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)
        except NetworkIPv4NotFoundError:
            return self.response_error(281)
        except EquipamentoNotFoundError:
            return self.response_error(117, ip_map.get('id_equipment'))
        except EnvironmentVipNotFoundError:
            return self.response_error(283)
        except UserNotAuthorizedError:
            return self.not_authorized()
        except XMLError, x:
            self.log.error(u'Error reading the XML request.')
            return self.response_error(3, x)
        except (IpError, NetworkIPv4Error, EquipamentoError, GrupoError), e:
            self.log.error(e)
            return self.response_error(1)
