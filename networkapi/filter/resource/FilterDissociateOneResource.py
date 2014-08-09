# -*- coding:utf-8 -*-
'''
Title: Infrastructure NetworkAPI
Author: csilva / S2IT
Copyright: ( c )  2009 globo.com todos os direitos reservados.
'''
from __future__ import with_statement
from networkapi.admin_permission import AdminPermission
from networkapi.rest import RestResource
from networkapi.filter.models import Filter, FilterError, FilterNotFoundError
from networkapi.filterequiptype.models import FilterEquipType, CantDissociateError
from networkapi.equipamento.models import TipoEquipamento, TipoEquipamentoNotFoundError
from networkapi.auth import has_perm
from networkapi.log import Log
from networkapi.util import is_valid_int_greater_zero_param
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.exception import InvalidValueError
from django.core.exceptions import ObjectDoesNotExist


class FilterDissociateOneResource(RestResource):

    '''Class that receives requests to remove association between Filter and TipoEquipamento.'''

    log = Log('FilterDissociateOneResource')

    def handle_put(self, request, user, *args, **kwargs):
        """Treat PUT requests to dissociate Filter and TipoEquipamento.

        URL: filter/<id_filter>/dissociate/<id_equip_type>
        """

        try:
            self.log.info("")
            # Commons Validations

            # User permission
            if not has_perm(
                    user,
                    AdminPermission.ENVIRONMENT_MANAGEMENT,
                    AdminPermission.WRITE_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                return self.not_authorized()

            if not is_valid_int_greater_zero_param(kwargs['id_filter']):
                self.log.error(
                    u'Parameter id_filter is invalid. Value: %s.',
                    kwargs['id_filter'])
                raise InvalidValueError(None, 'id_filter', kwargs['id_filter'])
            else:
                # Check existence
                fil = Filter().get_by_pk(kwargs['id_filter'])

            if not is_valid_int_greater_zero_param(kwargs['id_equip_type']):
                self.log.error(
                    u'Parameter id_equip_type is invalid. Value: %s.',
                    kwargs['id_equip_type'])
                raise InvalidValueError(
                    None,
                    'id_equip_type',
                    kwargs['id_equip_type'])
            else:
                # Check existence
                eq_tp = TipoEquipamento().get_by_pk(kwargs['id_equip_type'])

            # Delete association
            try:
                association = FilterEquipType.objects.get(
                    filter=fil.id,
                    equiptype=eq_tp.id)

                ## Only delete if there's no conflicts ##
                association.delete(user)

            except ObjectDoesNotExist as e:
                # Association doesn't exist, ok
                self.log.error(e)
                pass

            return self.response(dumps_networkapi({}))

        except CantDissociateError as e:
            return self.response_error(
                348,
                e.cause['equiptype'],
                e.cause['filter_name'])
        except InvalidValueError as e:
            return self.response_error(269, e.param, e.value)
        except TipoEquipamentoNotFoundError as e:
            return self.response_error(100)
        except FilterNotFoundError as e:
            return self.response_error(339)
        except FilterError as e:
            return self.response_error(1)
        except BaseException as e:
            return self.response_error(1)
