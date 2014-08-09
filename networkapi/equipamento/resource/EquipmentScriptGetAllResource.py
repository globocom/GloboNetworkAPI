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
from networkapi.equipamento.models import EquipamentoRoteiro, EquipamentoError


class EquipmentScriptGetAllResource(RestResource):

    log = Log('EquipmentScriptGetAllResource')

    def handle_get(self, request, user, *args, **kwargs):
        """Treat requests GET to list all Equipment Script.

        URL: equipmentscript/all
        """
        try:
            self.log.info("GET to list all Equipment Script")

            # User permission
            if not has_perm(user, AdminPermission.EQUIPMENT_MANAGEMENT, AdminPermission.READ_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                raise UserNotAuthorizedError(None)

            map_list = []
            for equipment_script in EquipamentoRoteiro.search(user.grupos.all()):
                equip_map = dict()
                equip_map['id'] = equipment_script.equipamento.id
                equip_map['nome'] = equipment_script.equipamento.nome
                equip_map[
                    'id_tipo_equipamento'] = equipment_script.equipamento.tipo_equipamento.id
                equip_map[
                    'nome_tipo_equipamento'] = equipment_script.equipamento.tipo_equipamento.tipo_equipamento
                equip_map['id_modelo'] = equipment_script.equipamento.modelo.id
                equip_map[
                    'nome_modelo'] = equipment_script.equipamento.modelo.nome
                equip_map[
                    'id_marca'] = equipment_script.equipamento.modelo.marca.id
                equip_map[
                    'nome_marca'] = equipment_script.equipamento.modelo.marca.nome

                script_map = dict()
                script_map['id'] = equipment_script.roteiro.id
                script_map['nome'] = equipment_script.roteiro.roteiro
                script_map['descricao'] = equipment_script.roteiro.descricao
                script_map[
                    'id_tipo_roteiro'] = equipment_script.roteiro.tipo_roteiro.id
                script_map[
                    'nome_tipo_roteiro'] = equipment_script.roteiro.tipo_roteiro.tipo
                script_map[
                    'descricao_tipo_roteiro'] = equipment_script.roteiro.tipo_roteiro.descricao

                equip_script_map = dict()
                equip_script_map['equipamento'] = equip_map
                equip_script_map['roteiro'] = script_map

                if equip_script_map not in map_list:
                    map_list.append(equip_script_map)

            return self.response(dumps_networkapi({'equipamento_roteiro': map_list}))

        except UserNotAuthorizedError:
            return self.not_authorized()
        except EquipamentoError:
            return self.response_error(1)
