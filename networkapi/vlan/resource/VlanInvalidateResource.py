# -*- coding:utf-8 -*-
'''
Title: Infrastructure NetworkAPI
Author: masilva / s2it
Copyright: ( c )  2009 globo.com todos os direitos reservados.
'''
from __future__ import with_statement
from networkapi.admin_permission import AdminPermission
from networkapi.auth import has_perm
from networkapi.exception import InvalidValueError
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.log import Log
from networkapi.rest import RestResource, UserNotAuthorizedError
from networkapi.util import is_valid_int_greater_zero_param, is_valid_version_ip
from networkapi.vlan.models import VlanError, Vlan, VlanNotFoundError
from networkapi.ambiente.models import IP_VERSION
from networkapi.distributedlock import distributedlock, LOCK_VLAN


class VlanInvalidateResource(RestResource):

    log = Log('VlanInvalidateResource')

    def handle_put(self, request, user, *args, **kwargs):
        '''Treat PUT requests to Invalidate a vlan 

        URL: vlan/<id_vlan>/invalidate/<network>
        '''

        try:

            id_vlan = kwargs.get('id_vlan')

            network = kwargs.get('network')

            # User permission
            if not has_perm(user, AdminPermission.ACL_VLAN_VALIDATION, AdminPermission.WRITE_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                raise UserNotAuthorizedError(None)

            # Valid Vlan ID
            if not is_valid_int_greater_zero_param(id_vlan):
                self.log.error(
                    u'The id_vlan parameter is not a valid value: %s.', id_vlan)
                raise InvalidValueError(None, 'vlan_id', id_vlan)

            # Valid Network
            if not is_valid_version_ip(network, IP_VERSION):
                self.log.error(
                    u'The network parameter is not a valid value: %s.', network)
                raise InvalidValueError(None, 'network', network)

            # Find Vlan by ID to check if it exist
            vlan = Vlan().get_by_pk(id_vlan)

            with distributedlock(LOCK_VLAN % id_vlan):

                # Set Values
                if network == IP_VERSION.IPv4[0]:
                    vlan.acl_valida = 0
                    vlan.acl_file_name = None

                else:
                    vlan.acl_valida_v6 = 0
                    vlan.acl_file_name_v6 = None

                vlan.save(user)

                return self.response(dumps_networkapi({}))

        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)

        except UserNotAuthorizedError:
            return self.not_authorized()

        except VlanNotFoundError, e:
            return self.response_error(116)

        except VlanError, e:
            return self.response_error(1)
