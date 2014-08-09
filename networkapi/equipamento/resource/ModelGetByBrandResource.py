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
from networkapi.equipamento.models import Marca, Modelo, EquipamentoError, MarcaNotFoundError
from networkapi.exception import InvalidValueError
from networkapi.util import is_valid_int_greater_zero_param


class ModelGetByBrandResource(RestResource):

    log = Log('ModelGetByBrandResource')

    def handle_get(self, request, user, *args, **kwargs):
        """Treat requests GET to list all the Model by Brand.

        URL: model/brand/<id_brand>/
        """
        try:

            self.log.info("GET to list all the Model by Brand")

            # User permission
            if not has_perm(
                    user,
                    AdminPermission.BRAND_MANAGEMENT,
                    AdminPermission.READ_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                raise UserNotAuthorizedError(None)

            id_brand = kwargs.get('id_brand')

            # Valid ID Brand
            if not is_valid_int_greater_zero_param(id_brand):
                self.log.error(
                    u'The id_brand parameter is not a valid value: %s.',
                    id_brand)
                raise InvalidValueError(None, 'id_groupl3', id_brand)

            # Find Brand by ID to check if it exist
            Marca.get_by_pk(id_brand)

            model_list = []
            for model in Modelo.get_by_brand(id_brand):
                model_map = dict()
                model_map['id'] = model.id
                model_map['nome'] = model.nome
                model_map['id_marca'] = model.marca.id
                model_map['nome_marca'] = model.marca.nome
                model_list.append(model_map)

            return self.response(dumps_networkapi({'model': model_list}))

        except InvalidValueError as e:
            return self.response_error(269, e.param, e.value)

        except UserNotAuthorizedError:
            return self.not_authorized()

        except MarcaNotFoundError:
            return self.response_error(167, id_brand)

        except EquipamentoError:
            return self.response_error(1)
