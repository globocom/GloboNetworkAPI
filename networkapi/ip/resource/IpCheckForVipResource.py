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
import logging

from django.forms.models import model_to_dict

from networkapi.admin_permission import AdminPermission
from networkapi.ambiente.models import EnvironmentVip
from networkapi.auth import has_perm
from networkapi.exception import EnvironmentVipNotFoundError
from networkapi.exception import InvalidValueError
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.infrastructure.xml_utils import loads
from networkapi.infrastructure.xml_utils import XMLError
from networkapi.ip.models import Ip
from networkapi.ip.models import IpError
from networkapi.ip.models import IpNotAvailableError
from networkapi.ip.models import IpNotFoundError
from networkapi.ip.models import Ipv6
from networkapi.ip.models import NetworkNotInEvip
from networkapi.rest import RestResource
from networkapi.rest import UserNotAuthorizedError
from networkapi.util import is_valid_int_greater_zero_param
from networkapi.util import is_valid_ipv4
from networkapi.util import is_valid_ipv6


class IpCheckForVipResource(RestResource):

    log = logging.getLogger('IpCheckForVipResource')

    def handle_post(self, request, user, *args, **kwargs):
        """Handles POST requests to check an IPv4 or Ipv6 for vip request.

        URL: ip/checkvipip/
        """
        self.log.info('Check a Ipv4 or Ipv6 for Vip')

        from networkapi.equipamento.models import TipoEquipamento

        try:

            # Business Validations

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
            ip = ip_map.get('ip')
            id_evip = ip_map.get('id_evip')

            # User permission
            if not has_perm(user, AdminPermission.IPS, AdminPermission.READ_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                return self.not_authorized()

            # Valid ip id
            if ip is None:
                self.log.error(u'Parameter ip is invalid. Value: %s.', ip)
                raise InvalidValueError(None, 'ip', ip)

            # Valid evip id
            if not is_valid_int_greater_zero_param(id_evip):
                raise InvalidValueError(None, 'id_evip', id_evip)

            # Business Rules

            evip = EnvironmentVip.get_by_pk(id_evip)

            ip_list = ip.split('.')

            if len(ip_list) == 1:

                if not is_valid_ipv6(ip):
                    self.log.error(u'Parameter ip is invalid. Value: %s.', ip)
                    raise InvalidValueError(None, 'ip', ip)

                if len(evip.networkipv6_set.all()) <= 0:
                    raise NetworkNotInEvip(
                        'IPv6', 'Não há rede no ambiente vip fornecido')

                ip_list = ip.split(':')
                ip_checked = Ipv6.get_by_octs_and_environment_vip(ip_list[0], ip_list[1], ip_list[
                                                                  2], ip_list[3], ip_list[4], ip_list[5], ip_list[6], ip_list[7], id_evip)

                ip_ok = False

                for ip_equip in ip_checked.ipv6equipament_set.all():

                    if ip_equip.equipamento.tipo_equipamento == TipoEquipamento.get_tipo_balanceador():

                        ip_ok = True
                        break

                if not ip_ok:
                    raise IpNotAvailableError(
                        None, 'Ipv6 indisponível para o Ambiente Vip: %s, pois não existe equipamento do Tipo Balanceador relacionado a este Ip.' % evip.show_environment_vip())

            else:

                if not is_valid_ipv4(ip):
                    self.log.error(u'Parameter ip is invalid. Value: %s.', ip)
                    raise InvalidValueError(None, 'ip', ip)

                if len(evip.networkipv4_set.all()) <= 0:
                    raise NetworkNotInEvip(
                        'IPv4', 'Não há rede no ambiente vip fornecido')

                ip_checked = Ip.get_by_octs_and_environment_vip(
                    ip_list[0], ip_list[1], ip_list[2], ip_list[3], id_evip)

                ip_ok = False

                for ip_equip in ip_checked.ipequipamento_set.all():

                    if ip_equip.equipamento.tipo_equipamento == TipoEquipamento.get_tipo_balanceador():

                        ip_ok = True
                        break

                if not ip_ok:
                    raise IpNotAvailableError(
                        None, 'Ipv4 indisponível para o Ambiente Vip: %s, pois não existe equipamento do Tipo Balanceador relacionado a este Ip.' % evip.show_environment_vip())

            ip_dict = model_to_dict(ip_checked)

            return self.response(dumps_networkapi({'ip': ip_dict}))

        except NetworkNotInEvip, e:
            return self.response_error(321, e.cause)
        except IpNotAvailableError, e:
            return self.response_error(150, e.message)
        except XMLError, x:
            self.log.error(u'Error reading the XML request.')
            return self.response_error(3, x)
        except EnvironmentVipNotFoundError, e:
            return self.response_error(283)
        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)
        except UserNotAuthorizedError:
            return self.not_authorized()
        except IpNotFoundError, e:
            return self.response_error(334, e.message)
        except (IpError):
            return self.response_error(1)
