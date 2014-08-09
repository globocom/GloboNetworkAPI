# -*- coding:utf-8 -*-
'''
Title: Infrastructure NetworkAPI
Author: avanzolin / TQI
Copyright: ( c )  2009 globo.com todos os direitos reservados.
'''

from networkapi.rest import RestResource
from networkapi.auth import has_perm
from networkapi.admin_permission import AdminPermission
from networkapi.infrastructure.xml_utils import loads, XMLError, dumps_networkapi
from networkapi.log import Log
from networkapi.grupo.models import GrupoError
from networkapi.equipamento.models import EquipamentoNotFoundError, EquipamentoError
from networkapi.exception import InvalidValueError
from networkapi.equipamento.models import Equipamento
from networkapi.util import is_valid_string_maxsize


class EquipScriptListResource(RestResource):

    log = Log('EquipScriptListResource')

    def handle_post(self, request, user, *args, **kwargs):
        """Handles POST requests to list all equip scripts by equipment name.

        URLs: equipamentoroteiro/name/
        """

        try:

            # Commons Validations

            # User permission
            if not has_perm(
                    user,
                    AdminPermission.EQUIPMENT_MANAGEMENT,
                    AdminPermission.READ_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                return self.not_authorized()

            # Business Validations

            # Load XML data
            xml_map, attrs_map = loads(request.raw_post_data)

            # XML data format
            networkapi_map = xml_map.get('networkapi')
            if networkapi_map is None:
                msg = u'There is no value to the networkapi tag of XML request.'
                self.log.error(msg)
                return self.response_error(3, msg)
            equip_script_map = networkapi_map.get('equipamento_roteiro')
            if equip_script_map is None:
                msg = u'There is no value to the equipamento_roteiro tag of XML request.'
                self.log.error(msg)
                return self.response_error(3, msg)

            # Get XML data
            name = equip_script_map.get('name')

            # Name must NOT be none and 50 is the maxsize
            if not is_valid_string_maxsize(name, 50):
                self.log.error(u'Parameter name is invalid. Value: %s.', name)
                raise InvalidValueError(None, 'name', name)

            # Equipment
            try:

                # Find equipment by name to check if it exist
                equip = Equipamento.get_by_name(name)

            except EquipamentoNotFoundError as e:
                return self.response_error(117, name)

            # Business Rules

            # List access related with equip
            equip_script_list = equip.equipamentoroteiro_set.all()
            # Permissions
            equip_script_list = equip_script_list.filter(
                equipamento__grupos__direitosgrupoequipamento__ugrupo__in=user.grupos.all(),
                equipamento__grupos__direitosgrupoequipamento__escrita='1')

            map_dicts = []
            for equip_script in equip_script_list:
                es_map = dict()
                es_map['id'] = equip_script.id
                es_map['roteiro_id'] = equip_script.roteiro.id
                es_map['roteiro_name'] = equip_script.roteiro.roteiro
                es_map['roteiro_desc'] = equip_script.roteiro.descricao
                es_map[
                    'tipo_roteiro_id'] = equip_script.roteiro.tipo_roteiro.id
                es_map[
                    'tipo_roteiro_name'] = equip_script.roteiro.tipo_roteiro.tipo
                es_map[
                    'tipo_roteiro_desc'] = equip_script.roteiro.tipo_roteiro.descricao
                map_dicts.append(es_map)

            equip_map = dict()
            equip_map['id'] = equip.id
            equip_map['name'] = equip.nome

            equip_script_map = dict()
            equip_script_map['equipamento_roteiro'] = map_dicts
            equip_script_map['equipamento'] = equip_map

            # Return XML
            return self.response(dumps_networkapi(equip_script_map))

        except InvalidValueError as e:
            return self.response_error(269, e.param, e.value)
        except (EquipamentoError, GrupoError):
            return self.response_error(1)
        except XMLError as x:
            self.log.error(u'Error reading the XML request.')
            return self.response_error(3, x)
