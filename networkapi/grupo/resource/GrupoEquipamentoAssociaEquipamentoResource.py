# -*- coding:utf-8 -*-
'''
Title: Infrastructure NetworkAPI
Author: globo.com / TQI
Copyright: ( c )  2009 globo.com todos os direitos reservados.
'''

from networkapi.rest import RestResource, UserNotAuthorizedError

from networkapi.auth import has_perm

from networkapi.admin_permission import AdminPermission

from networkapi.infrastructure.xml_utils import loads, XMLError, dumps_networkapi

from networkapi.log import Log

from networkapi.equipamento.models import *

from networkapi.roteiro.models import *

from networkapi.ambiente.models import *

from networkapi.grupo.models import EGrupoNotFoundError, GrupoError
from networkapi.util import is_valid_int_greater_zero_param,\
    is_valid_string_minsize
import re


class GrupoEquipamentoAssociaEquipamentoResource(RestResource):

    log = Log('EquipamentoGrupoAssociaEquipamentoResource')

    def handle_post(self, request, user, *args, **kwargs):
        """Trata uma requisicao POST para inserir um associao entre grupo de equipamento e equipamento.

        URL: equipmentogrupo/associa
        """

        try:
            # Load XML data
            xml_map, attrs_map = loads(request.raw_post_data)

            # XML data format
            networkapi_map = xml_map.get('networkapi')
            if networkapi_map is None:
                msg = u'There is no value to the networkapi tag of XML request.'
                self.log.error(msg)
                return self.response_error(3, msg)
            equip_map = networkapi_map.get('equipamento_grupo')
            if equip_map is None:
                msg = u'There is no value to the ip tag of XML request.'
                self.log.error(msg)
                return self.response_error(3, msg)

            # Get XML data
            equip_id = equip_map.get('id_equipamento')
            id_grupo = equip_map.get('id_grupo')

            # Valid equip_id
            if not is_valid_int_greater_zero_param(equip_id):
                self.log.error(
                    u'Parameter equip_id is invalid. Value: %s.',
                    equip_id)
                raise InvalidValueError(None, 'equip_id', equip_id)

            # Valid id_modelo
            if not is_valid_int_greater_zero_param(id_grupo):
                self.log.error(
                    u'Parameter id_grupo is invalid. Value: %s.',
                    id_grupo)
                raise InvalidValueError(None, 'id_modelo', id_grupo)

            if not has_perm(user,
                            AdminPermission.EQUIPMENT_MANAGEMENT,
                            AdminPermission.WRITE_OPERATION,
                            id_grupo,
                            equip_id,
                            AdminPermission.EQUIP_WRITE_OPERATION):
                raise UserNotAuthorizedError(
                    None,
                    u'User does not have permission to perform the operation.')

            # Business Rules

            # New IP
            equip = Equipamento()
            equip = equip.get_by_pk(equip_id)
            egrupo = EGrupo.get_by_pk(id_grupo)
            tipo_equipamento = TipoEquipamento()

            try:
                if ((int(egrupo.GRUPO_EQUIPAMENTO_ORQUESTRACAO) == int(id_grupo)) and (
                        int(equip.tipo_equipamento.id) != int(tipo_equipamento.TIPO_EQUIPAMENTO_SERVIDOR_VIRTUAL))):
                    raise EquipamentoError(
                        None,
                        "Equipamentos que não sejam do tipo 'Servidor Virtual' não podem fazer parte do grupo 'Equipamentos Orquestração'.")
            except EquipamentoError as e:
                return self.response_error(150, e.message)

            equipamento_grupo = EquipamentoGrupo()
            equipamento_grupo.egrupo = egrupo
            equipamento_grupo.equipamento = equip
            equipamento_grupo.create(user)

            map = dict()
            map['id'] = equipamento_grupo.id
            map_return = dict()
            lista = []
            lista.append(map)
            map_return['grupo'] = lista

            return self.response(dumps_networkapi(map_return))

        except InvalidValueError as e:
            return self.response_error(269, e.param, e.value)
        except UserNotAuthorizedError:
            return self.not_authorized()
        except TipoEquipamentoNotFoundError as e:
            return self.response_error(150, e.message)
        except ModeloNotFoundError as e:
            return self.response_error(150, e.message)
        except EquipamentoNotFoundError as e:
            return self.response_error(117, equip_id)
        except EquipamentoNameDuplicatedError as e:
            return self.response_error(e.message)
        except EquipamentoError as e:
            return self.response_error(150, e.message)
        except XMLError as x:
            self.log.error(u'Error reading the XML request.')
            return self.response_error(3, x)
