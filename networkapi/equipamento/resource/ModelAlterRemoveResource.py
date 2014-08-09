# -*- coding:utf-8 -*-
'''
Title: Infrastructure NetworkAPI
Author: masilva / S2IT
Copyright: ( c )  2009 globo.com todos os direitos reservados.
'''

from __future__ import with_statement
from networkapi.admin_permission import AdminPermission
from networkapi.auth import has_perm
from networkapi.distributedlock import distributedlock, LOCK_MODEL
from networkapi.exception import InvalidValueError
from networkapi.equipamento.models import Marca, MarcaNotFoundError, EquipamentoError, Modelo, ModeloNotFoundError, MarcaModeloNameDuplicatedError, ModeloUsedByEquipamentoError
from networkapi.infrastructure.xml_utils import loads, dumps_networkapi
from networkapi.log import Log
from networkapi.rest import RestResource, UserNotAuthorizedError
from networkapi.util import is_valid_int_greater_zero_param, is_valid_string_minsize, is_valid_string_maxsize


class ModelAlterRemoveResource(RestResource):

    log = Log('ModelAlterRemoveResource')

    def handle_put(self, request, user, *args, **kwargs):
        """Treat requests PUT to edit Model.

        URL: model/<id_model>/
        """
        try:

            self.log.info("Edit Model")

            # User permission
            if not has_perm(
                    user,
                    AdminPermission.BRAND_MANAGEMENT,
                    AdminPermission.WRITE_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                raise UserNotAuthorizedError(None)

            id_model = kwargs.get('id_model')

            # Load XML data
            xml_map, attrs_map = loads(request.raw_post_data)

            # XML data format

            networkapi_map = xml_map.get('networkapi')
            if networkapi_map is None:
                return self.response_error(
                    3,
                    u'There is no value to the networkapi tag  of XML request.')

            model_map = networkapi_map.get('model')
            if model_map is None:
                return self.response_error(
                    3,
                    u'There is no value to the model tag  of XML request.')

            # Get XML data
            name = model_map.get('name')
            id_brand = model_map.get('id_brand')

            # Valid ID Model
            if not is_valid_int_greater_zero_param(id_model):
                self.log.error(
                    u'The id_model parameter is not a valid value: %s.',
                    id_model)
                raise InvalidValueError(None, 'id_model', id_model)

            # Valid name
            if not is_valid_string_minsize(
                    name,
                    3) or not is_valid_string_maxsize(
                    name,
                    100):
                self.log.error(u'Parameter name is invalid. Value: %s', name)
                raise InvalidValueError(None, 'name', name)

            # Valid ID Brand
            if not is_valid_int_greater_zero_param(id_brand):
                self.log.error(
                    u'The id_brand parameter is not a valid value: %s.',
                    id_brand)
                raise InvalidValueError(None, 'id_brand', id_brand)

            # Find Brand by ID to check if it exist
            brand = Marca.get_by_pk(id_brand)

            # Find Model by ID to check if it exist
            model = Modelo.get_by_pk(id_model)

            with distributedlock(LOCK_MODEL % id_model):

                try:

                    if not (
                            model.nome.lower() == name.lower() and model.marca.id == id_brand):
                        Modelo.get_by_name_brand(name, id_brand)
                        raise MarcaModeloNameDuplicatedError(
                            None, u'Já existe um modelo com o nome %s com marca %s.' %
                            (name, brand.nome))
                except ModeloNotFoundError:
                    pass

                # set variables
                model.nome = name
                model.marca = brand

                try:
                    # update Model
                    model.save(user)
                except Exception as e:
                    self.log.error(u'Failed to update the Model.')
                    raise EquipamentoError(e, u'Failed to update the Model.')

                return self.response(dumps_networkapi({}))

        except InvalidValueError as e:
            return self.response_error(269, e.param, e.value)

        except UserNotAuthorizedError:
            return self.not_authorized()

        except MarcaNotFoundError:
            return self.response_error(167, id_brand)

        except ModeloNotFoundError:
            return self.response_error(101)

        except MarcaModeloNameDuplicatedError:
            return self.response_error(252, name, id_brand)

        except EquipamentoError:
            return self.response_error(1)

    def handle_delete(self, request, user, *args, **kwargs):
        """Treat requests DELETE to remove Model.

        URL: model/<id_model>/
        """
        try:

            self.log.info("Remove Model")

            # User permission
            if not has_perm(
                    user,
                    AdminPermission.BRAND_MANAGEMENT,
                    AdminPermission.WRITE_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                raise UserNotAuthorizedError(None)

            id_model = kwargs.get('id_model')

            # Valid ID Model
            if not is_valid_int_greater_zero_param(id_model):
                self.log.error(
                    u'The id_model parameter is not a valid value: %s.',
                    id_model)
                raise InvalidValueError(None, 'id_model', id_model)

            # Find Model by ID to check if it exist
            model = Modelo.get_by_pk(id_model)

            with distributedlock(LOCK_MODEL % id_model):

                try:

                    if model.equipamento_set.count() > 0:
                        raise ModeloUsedByEquipamentoError(
                            None,
                            u"O modelo %s tem equipamento associado." %
                            model.id)

                    # remove Model
                    model.delete(user)

                except ModeloUsedByEquipamentoError as e:
                    raise e
                except Exception as e:
                    self.log.error(u'Failed to remove the Model.')
                    raise EquipamentoError(e, u'Failed to remove the Model.')

                return self.response(dumps_networkapi({}))

        except InvalidValueError as e:
            return self.response_error(269, e.param, e.value)

        except UserNotAuthorizedError:
            return self.not_authorized()

        except ModeloNotFoundError:
            return self.response_error(101)

        except ModeloUsedByEquipamentoError:
            return self.response_error(202, id_model)

        except EquipamentoError:
            return self.response_error(1)
