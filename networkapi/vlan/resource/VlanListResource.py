# -*- coding:utf-8 -*-
"""
Title: Infrastructure NetworkAPI
Author: avanzolin / S2it
Copyright: ( c )  2009 globo.com todos os direitos reservados.
"""

from networkapi.admin_permission import AdminPermission
from networkapi.auth import has_perm
from networkapi.grupo.models import GrupoError
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.log import Log
from networkapi.rest import RestResource
from networkapi.vlan.models import Vlan, VlanError


class VlanListResource(RestResource):

    log = Log('VlanListResource')

    def handle_get(self, request, user, *args, **kwargs):
        """Handles POST requests to list all VLANs.

        URLs: /vlan/all/
        """

        self.log.info('List all VLANs')

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

            # Business Rules

            vlans = Vlan.objects.select_related().all()

            vlan_list = []

            for vlan in vlans:
                model_dict = dict()
                model_dict['id'] = vlan.id
                model_dict['name'] = vlan.nome
                model_dict['num_vlan'] = vlan.num_vlan
                model_dict["environment"] = vlan.ambiente.divisao_dc.nome + " - " + \
                    vlan.ambiente.ambiente_logico.nome + " - " + vlan.ambiente.grupo_l3.nome

                vlan_list.append(model_dict)

            return self.response(dumps_networkapi({'vlan': vlan_list}))

        except (VlanError, GrupoError) as e:
            self.log.error(e)
            return self.response_error(1)
        except BaseException as e:
            self.log.error(e)
            return self.response_error(1)
