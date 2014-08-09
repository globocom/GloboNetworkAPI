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
from networkapi.ip.models import NetworkIPv4NotFoundError, NetworkIPv4Error, NetworkIPv4


class NetworkIPv4GetResource(RestResource):

    log = Log('NetworkIPv4GetResource')

    def handle_get(self, request, user, *args, **kwargs):
        """Handles GET requests to list all network IPv4 by network ipv4 id.

        URLs: network/ipv4/id/id_rede4
         """

        try:

            # Commons Validations

            # User permission
            if not has_perm(
                    user,
                    AdminPermission.VLAN_MANAGEMENT,
                    AdminPermission.READ_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                return self.not_authorized()

            # Business Validations

            # Valid id access
            id_network = kwargs.get('id_rede4')

            if not is_valid_int_greater_zero_param(id_network):
                self.log.error(
                    u'Parameter id_rede is invalid. Value: %s.',
                    id_network)
                raise InvalidValueError(None, 'id_rede4', id_network)

            # Business Rules

            network = NetworkIPv4.get_by_pk(id_network)

            network_map = dict()
            network_map['network'] = model_to_dict(network)

            # Return XML
            return self.response(dumps_networkapi(network_map))

        except InvalidValueError as e:
            return self.response_error(269, e.param, e.value)
        except NetworkIPv4NotFoundError as e:
            return self.response_error(281)
        except (NetworkIPv4Error):
            return self.response_error(1)
        except XMLError as x:
            self.log.error(u'Error reading the XML request.')
            return self.response_error(3, x)
