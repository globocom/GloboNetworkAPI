# -*- coding:utf-8 -*-
'''
Title: Infrastructure NetworkAPI
Author: masilva / S2it
Copyright: ( c )  2009 globo.com todos os direitos reservados.
'''
from __future__ import with_statement
from networkapi.infrastructure.xml_utils import dumps_networkapi

from networkapi.ip.models import Equipamento, Ipv6, Ipv6Equipament, IpNotFoundError, IpEquipmentNotFoundError, IpEquipamentoDuplicatedError, IpError, IpCantBeRemovedFromVip, IpEquipCantDissociateFromVip

from networkapi.equipamento.models import EquipamentoNotFoundError, EquipamentoError

from networkapi.rest import RestResource, UserNotAuthorizedError

from networkapi.admin_permission import AdminPermission

from networkapi.auth import has_perm

from networkapi.log import Log

from networkapi.grupo.models import GrupoError

from networkapi.util import is_valid_int_greater_zero_param,\
    destroy_cache_function

from networkapi.exception import InvalidValueError

from networkapi.distributedlock import distributedlock, LOCK_IPV6
from django.db.utils import IntegrityError
from networkapi.requisicaovips.models import ServerPoolMember


class Ipv6RemoveResource(RestResource):

    log = Log('Ipv6RemoveResource')

    def handle_delete(self, request, user, *args, **kwargs):
        '''Treat DELETE requests to remove the relationship between IPv6 and equipment.

        URL: ipv6/<id_ipv6>/equipment/<id_equip>/remove/
        '''
        self.log.info("Remove an IPv6 to a equipament.")

        try:

            ipv6_id = kwargs.get('id_ipv6')
            equip_id = kwargs.get('id_equip')

            # Valid Ipv6 ID
            if not is_valid_int_greater_zero_param(ipv6_id):
                self.log.error(
                    u'The id_ipv6 parameter is not a valid value: %s.', ipv6_id)
                raise InvalidValueError(None, 'id_ipv6', ipv6_id)

            # Valid Ipv6 ID
            if not is_valid_int_greater_zero_param(equip_id):
                self.log.error(
                    u'The id_equip parameter is not a valid value: %s.', equip_id)
                raise InvalidValueError(None, 'id_equip', equip_id)

            # Find Equipament by ID to check if it exist
            Equipamento().get_by_pk(equip_id)

            # Find IPv6 by ID to check if it exist
            Ipv6().get_by_pk(ipv6_id)

            with distributedlock(LOCK_IPV6 % ipv6_id):

                # User permission
                if not has_perm(user, AdminPermission.IPS, AdminPermission.WRITE_OPERATION, None, equip_id, AdminPermission.EQUIP_WRITE_OPERATION):
                    self.log.error(
                        u'User does not have permission to perform the operation.')
                    raise UserNotAuthorizedError(None)

                ip = Ipv6().get_by_pk(ipv6_id)
                # Delete vlan's cache
                destroy_cache_function([ip.networkipv6.vlan_id])

                # delete equipment's cache
                destroy_cache_function([equip_id], True)

                # Remove Ipv6Equipament
                ipv6_equipament = Ipv6Equipament()

                if ServerPoolMember.objects.filter(ipv6=ip).count() != 0:
                    # IP associated with VIP
                    return self.response_error(354, ipv6_id)

                ipv6_equipament.remove(user, ipv6_id, equip_id)

                return self.response(dumps_networkapi({}))

        except IpCantBeRemovedFromVip, e:
            return self.response_error(319, "ip", 'ipv6', ipv6_id)

        except IpEquipCantDissociateFromVip, e:
            return self.response_error(352, e.cause['ip'], e.cause['equip_name'], e.cause['vip_id'])

        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)

        except IpNotFoundError:
            return self.response_error(119)

        except EquipamentoNotFoundError:
            return self.response_error(117, equip_id)

        except IpEquipmentNotFoundError:
            return self.response_error(288)

        except IpEquipamentoDuplicatedError:
            return self.response_error(120)

        except UserNotAuthorizedError:
            return self.not_authorized()

        except (IpError, EquipamentoError, GrupoError, IntegrityError), e:
            return self.response_error(1)
