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
from networkapi.ambiente.models import Ambiente
from django.forms.models import model_to_dict
from networkapi.util import is_valid_int_greater_zero_param
from networkapi.exception import InvalidValueError
from networkapi.equipamento.models import Equipamento, EquipamentoAmbiente,\
    EquipamentoNotFoundError


class EnvironmentGetByEquipResource(RestResource):

    log = Log('EnvironmentGetByEquipResource')

    def handle_get(self, request, user, *args, **kwargs):
        """Treat requests GET to list all Environments.

        URL: /ambiente/equip/id_equip
        """

        try:

            # Commons Validations

            # User permission

            if not has_perm(
                    user,
                    AdminPermission.ENVIRONMENT_MANAGEMENT,
                    AdminPermission.READ_OPERATION):
                return self.not_authorized()
            if not has_perm(
                    user,
                    AdminPermission.EQUIPMENT_MANAGEMENT,
                    AdminPermission.READ_OPERATION):
                return self.not_authorized()

            id_equip = kwargs.get('id_equip')

            if not is_valid_int_greater_zero_param(id_equip):
                raise InvalidValueError(None, 'id_equip', id_equip)

            # Business Rules
            equip = Equipamento.get_by_pk(id_equip)
            environments_list = EquipamentoAmbiente.get_by_equipment(equip.id)

            # Get all environments in DB
            lists_aux = []
            for environment in environments_list:
                env = Ambiente.get_by_pk(environment.ambiente.id)
                env_map = model_to_dict(env)
                env_map["grupo_l3_name"] = env.grupo_l3.nome
                env_map["ambiente_logico_name"] = env.ambiente_logico.nome
                env_map["divisao_dc_name"] = env.divisao_dc.nome
                env_map["is_router"] = environment.is_router

                if env.filter is not None:
                    env_map["filter_name"] = env.filter.name

                lists_aux.append(env_map)

            # Return XML
            environment_list = dict()
            environment_list["ambiente"] = lists_aux
            return self.response(dumps_networkapi(environment_list))

        except InvalidValueError as e:
            self.log.error(
                u'Parameter %s is invalid. Value: %s.',
                e.param,
                e.value)
            return self.response_error(269, e.param, e.value)
        except EquipamentoNotFoundError as e:
            return self.response_error(117, id_equip)
        except GrupoError:
            return self.response_error(1)
