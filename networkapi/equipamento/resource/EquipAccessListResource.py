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
from django.forms.models import model_to_dict


class EquipAccessListResource(RestResource):

    log = Log('EquipAccessListResource')

    def handle_post(self, request, user, *args, **kwargs):
        """Handles POST requests to list all equip access by equipment name.

        URLs: equipamentoacesso/name/
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
            equip_access_map = networkapi_map.get('equipamento_acesso')
            if equip_access_map is None:
                msg = u'There is no value to the vlan tag of XML request.'
                self.log.error(msg)
                return self.response_error(3, msg)

            # Get XML data
            name = equip_access_map.get('name')

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
            equip_access_list = equip.equipamentoacesso_set.all()
            # Permissions
            equip_access_list = equip_access_list.filter(
                equipamento__grupos__direitosgrupoequipamento__ugrupo__in=user.grupos.all(),
                equipamento__grupos__direitosgrupoequipamento__escrita='1')

            map_dicts = []
            for equip_acess in equip_access_list:
                equip_access_map = model_to_dict(equip_acess)
                if equip_access_map not in map_dicts:
                    map_dicts.append(equip_access_map)

            equip_access_map = dict()
            equip_access_map['equipamento_acesso'] = list(map_dicts)

            # Return XML
            return self.response(dumps_networkapi(equip_access_map))

        except InvalidValueError as e:
            return self.response_error(269, e.param, e.value)
        except (EquipamentoError, GrupoError):
            return self.response_error(1)
        except XMLError as x:
            self.log.error(u'Error reading the XML request.')
            return self.response_error(3, x)
