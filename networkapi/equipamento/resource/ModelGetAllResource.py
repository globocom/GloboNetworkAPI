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
from networkapi.equipamento.models import Modelo, EquipamentoError


class ModelGetAllResource(RestResource):

    log = Log('ModelGetAllResource')

    def handle_get(self, request, user, *args, **kwargs):
        """Treat requests GET to list all the Model.

        URL: model/all
        """
        try:

            self.log.info("GET to list all the Model")

            # User permission
            if not has_perm(
                    user,
                    AdminPermission.BRAND_MANAGEMENT,
                    AdminPermission.READ_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                raise UserNotAuthorizedError(None)

            model_list = []
            for model in Modelo.objects.all():
                model_map = dict()
                model_map['id'] = model.id
                model_map['nome'] = model.nome
                model_map['id_marca'] = model.marca.id
                model_map['nome_marca'] = model.marca.nome
                model_list.append(model_map)

            return self.response(dumps_networkapi({'model': model_list}))

        except UserNotAuthorizedError:
            return self.not_authorized()

        except EquipamentoError:
            return self.response_error(1)
