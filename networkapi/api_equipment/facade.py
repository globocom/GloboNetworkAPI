# -*- coding:utf-8 -*-
import logging

from networkapi.equipamento.models import Equipamento
from networkapi.equipamento.models import EquipamentoAmbiente
# from networkapi.admin_permission import AdminPermission
# from networkapi.auth import has_perm


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


def get_equipments_by_user(user, environment):
    """
    Return a list of equipments by user with rights of read
    :param user: Id user

    """
    eqpts = Equipamento.objects.filter(
        equipamentogrupo__egrupo__direitosgrupoequipamento__ugrupo__usuario=user,
        equipamentogrupo__egrupo__direitosgrupoequipamento__escrita=1
    )

    eqptsv4 = eqpts.filter(
        ipequipamento__ip__networkipv4__vlan__ambiente__environmentenvironmentvip__environment_vip__networkipv4__vlan__ambiente=environment
    )

    eqptsv6 = eqpts.filter(
        ipv6equipament__ip__networkipv6__vlan__ambiente__environmentenvironmentvip__environment_vip__networkipv6__vlan__ambiente=environment
    )

    eqpt = eqptsv4 | eqptsv6

    eqpt = eqpt.distinct()
    eqpt.prefetch_related(
        'ipequipamento_set__ip',
        'ipv6equipament_set__ipv6'
    )

    return eqpt


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
