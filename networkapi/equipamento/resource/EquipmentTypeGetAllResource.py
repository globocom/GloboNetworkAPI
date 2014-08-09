# -*- coding:utf-8 -*-
'''
Title: Infrastructure NetworkAPI
Author: masilva / S2IT
Copyright: ( c )  2012 globo.com todos os direitos reservados.
'''

from networkapi.admin_permission import AdminPermission
from networkapi.auth import has_perm
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.log import Log
from networkapi.rest import RestResource, UserNotAuthorizedError
from networkapi.equipamento.models import TipoEquipamento, EquipamentoError
from django.forms.models import model_to_dict


class EquipmentTypeGetAllResource(RestResource):

    log = Log('EquipmentTypeGetAllResource')

    def handle_get(self, request, user, *args, **kwargs):
        """Treat requests GET to list all Equipment Type.

        URL: equipmenttype/all
        """
        try:

            self.log.info("GET to list all Equipment Type")

            # User permission
            if not has_perm(
                    user,
                    AdminPermission.EQUIPMENT_MANAGEMENT,
                    AdminPermission.READ_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                raise UserNotAuthorizedError(None)

            map_list = []
            for equipment_type in TipoEquipamento.objects.all():
                eq_tp = {
                    'id': equipment_type.id,
                    'nome': equipment_type.tipo_equipamento}
                map_list.append(eq_tp)

            return self.response(
                dumps_networkapi({'equipment_type': map_list}))

        except UserNotAuthorizedError:
            return self.not_authorized()

        except EquipamentoError:
            return self.response_error(1)
