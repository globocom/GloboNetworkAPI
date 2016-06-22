# -*- coding:utf-8 -*-
import logging

# from networkapi.admin_permission import AdminPermission
# from networkapi.auth import has_perm
from networkapi.equipamento.models import Equipamento, EquipamentoAmbiente


log = logging.getLogger(__name__)


def all_equipments_are_in_maintenance(equipment_list):

    all_equips_in_maintenance = True
    for equipment in equipment_list:
        all_equips_in_maintenance &= equipment.maintenance

    return all_equips_in_maintenance


def get_routers_by_environment(environment_id):
    return EquipamentoAmbiente.objects.select_related('equipamento').filter(ambiente=environment_id, is_router=True)


def get_equipment_map(equipment):

    equipment_map = dict()
    equipment_map['id'] = equipment.id
    equipment_map['nome'] = equipment.nome
    equipment_map['tipo_equipamento'] = equipment.tipo_equipamento.tipo_equipamento
    equipment_map['modelo'] = equipment.modelo.nome
    equipment_map['marca'] = equipment.modelo.marca.nome
    equipment_map['maintenance'] = equipment.maintenance

    return equipment_map


def all_equipments_can_update_config(equipment_list, user):

    for equipment in equipment_list:
        res = Equipamento.objects.filter(
            equipamentogrupo__egrupo__direitosgrupoequipamento__ugrupo__usuariogrupo__usuario=user,
            equipamentogrupo__egrupo__direitosgrupoequipamento__alterar_config=True,
            id=equipment.id
        ).distinct()

        if not res:
            log.warning('User{} does not haver permission to Equipment {}'.format(
                user, equipment.id
            ))
            return False

    return True

    # other way
    # all_equipments_have_permission = True
    # for equipment in equipment_list:
    #     all_equipments_have_permission &= has_perm(
    #         user,
    #         AdminPermission.EQUIPMENT_MANAGEMENT,
    #         AdminPermission.WRITE_OPERATION,
    #         None,
    #         equipment.id,
    #         AdminPermission.EQUIP_UPDATE_CONFIG_OPERATION
    #     )
    # return all_equipments_have_permission
