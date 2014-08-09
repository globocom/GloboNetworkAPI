# -*- coding:utf-8 -*-
'''
Title: Infrastructure NetworkAPI
Author: avanzolin / S2it
Copyright: ( c )  2009 globo.com todos os direitos reservados.
'''
from __future__ import with_statement
from networkapi.admin_permission import AdminPermission
from networkapi.auth import has_perm
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.log import Log
from networkapi.rest import RestResource, UserNotAuthorizedError
from networkapi.util import is_valid_int_greater_zero_param,\
    destroy_cache_function
from networkapi.exception import InvalidValueError
from networkapi.ip.models import NetworkIPv4, NetworkIPv4NotFoundError, IpEquipamento
from networkapi.requisicaovips.models import RequisicaoVips
from networkapi.distributedlock import distributedlock, LOCK_NETWORK_IPV4
from networkapi.ip.models import IpCantBeRemovedFromVip
from networkapi.equipamento.models import EquipamentoAmbienteNotFoundError
from django.db.utils import IntegrityError
from networkapi.requisicaovips.models import ServerPoolMember
from networkapi.equipamento.models import Equipamento


class NetworkIPv4DeallocateResource(RestResource):

    log = Log('NetworkIPv4DeallocateResource')

    def handle_delete(self, request, user, *args, **kwargs):
        '''Handles DELETE requests to deallocate all relationships between NetworkIPv4.

        URL: network/ipv4/<id_network_ipv4>/deallocate/
        '''

        self.log.info("Deallocate all relationships between NetworkIPv4.")

        try:

            # Commons Validations

            # User permission
            if not has_perm(
                    user,
                    AdminPermission.VLAN_MANAGEMENT,
                    AdminPermission.WRITE_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                return self.not_authorized()

            # Business Validations

            # Load URL param
            network_ipv4_id = kwargs.get('id_network_ipv4')

            # Valid NetworkIpv4 ID
            if not is_valid_int_greater_zero_param(network_ipv4_id):
                self.log.error(
                    u'Parameter id_network_ipv4 is invalid. Value: %s.',
                    network_ipv4_id)
                raise InvalidValueError(
                    None,
                    'id_network_ipv4',
                    network_ipv4_id)

            # Existing NetworkIpv4 ID
            network_ipv4 = NetworkIPv4().get_by_pk(network_ipv4_id)

            for ipv4 in network_ipv4.ip_set.all():
                if ServerPoolMember.objects.filter(ip=ipv4).count() != 0:
                    # IP associated with VIP
                    return self.response_error(355, network_ipv4_id)

            with distributedlock(LOCK_NETWORK_IPV4 % network_ipv4_id):

                destroy_cache_function([network_ipv4.vlan_id])
                key_list_eqs = Equipamento.objects.filter(
                    ipequipamento__ip__networkipv4=network_ipv4).values_list(
                    'id',
                    flat=True)
                destroy_cache_function(key_list_eqs, True)
                # Business Rules
                # Remove NetworkIPv4 (will remove all relationships by cascade)
                network_ipv4.delete(user)

                # Return nothing
                return self.response(dumps_networkapi({}))

        except EquipamentoAmbienteNotFoundError as e:
            return self.response_error(320)
        except IpCantBeRemovedFromVip as e:
            return self.response_error(
                319,
                "network",
                "networkipv4",
                network_ipv4_id)
        except InvalidValueError as e:
            return self.response_error(269, e.param, e.value)
        except NetworkIPv4NotFoundError as e:
            return self.response_error(281)
        except UserNotAuthorizedError as e:
            return self.not_authorized()
        except Exception as e:
            if isinstance(e, IntegrityError):
                # IP associated VIP
                self.log.error(u'Failed to update the request vip.')
                return self.response_error(355, network_ipv4_id)
            else:
                return self.response_error(1)
