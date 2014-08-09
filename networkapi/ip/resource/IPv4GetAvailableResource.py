# -*- coding:utf-8 -*-
'''
Title: Infrastructure NetworkAPI
Author: avanzolin / TQI
Copyright: ( c )  2009 globo.com todos os direitos reservados.
'''

from networkapi.admin_permission import AdminPermission
from networkapi.auth import has_perm
from networkapi.equipamento.models import EquipamentoError
from networkapi.grupo.models import GrupoError
from networkapi.infrastructure.xml_utils import XMLError, dumps_networkapi
from networkapi.ip.models import NetworkIPv4NotFoundError, Ip, IpNotAvailableError, IpError, NetworkIPv4Error
from networkapi.log import Log
from networkapi.rest import RestResource, UserNotAuthorizedError
from networkapi.exception import InvalidValueError
from networkapi.util import is_valid_int_greater_zero_param


class IPv4GetAvailableResource(RestResource):

    log = Log('IPv4GetAvailableResource')

    def handle_get(self, request, user, *args, **kwargs):
        '''Handles GET requests get an IP4 available.

        URL: ip/availableip4/ip_rede
        '''

        self.log.info('Get an IP4 available')

        try:

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
            id_network = kwargs.get('id_rede')

            if not is_valid_int_greater_zero_param(id_network):
                self.log.error(
                    u'Parameter id_rede is invalid. Value: %s.',
                    id_network)
                raise InvalidValueError(None, 'id_rede', id_network)

            # Business Rules

            ip = Ip.get_available_ip(id_network)

            list_ip = []
            list_ip.append(ip)
            network_map = dict()
            map_aux = dict()
            map_aux['ip'] = list_ip

            network_map['ip'] = map_aux

            # Business Rules

            return self.response(dumps_networkapi(network_map))

        except InvalidValueError as e:
            return self.response_error(269, e.param, e.value)
        except NetworkIPv4NotFoundError:
            return self.response_error(281)
        except IpNotAvailableError as e:
            return self.response_error(150, e.message)
        except UserNotAuthorizedError:
            return self.not_authorized()
        except XMLError as x:
            self.log.error(u'Error reading the XML request.')
            return self.response_error(3, x)
        except (IpError, NetworkIPv4Error, EquipamentoError, GrupoError):
            return self.response_error(1)
