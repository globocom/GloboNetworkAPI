# -*- coding:utf-8 -*-
import logging

from django.db.models import Q

from networkapi.equipamento.models import Equipamento
from networkapi.equipamento.models import EquipamentoAmbiente
from networkapi.infrastructure.datatable import build_query_to_datatable_v3


# from networkapi.admin_permission import AdminPermission
# from networkapi.auth import has_perm


log = logging.getLogger(__name__)


def all_equipments_are_in_maintenance(equipment_list):

    all_equips_in_maintenance = True
    for equipment in equipment_list:
        all_equips_in_maintenance &= equipment.maintenance

    return all_equips_in_maintenance


def get_routers_by_environment(environment_id):
    return EquipamentoAmbiente.objects.select_related(
        'equipamento').filter(ambiente=environment_id, is_router=True)


def get_equipment_map(equipment):

    equipment_map = dict()
    equipment_map['id'] = equipment.id
    equipment_map['nome'] = equipment.nome
    equipment_map['tipo_equipamento'] = equipment.tipo_equipamento.tipo_equipamento
    equipment_map['modelo'] = equipment.modelo.nome
    equipment_map['marca'] = equipment.modelo.marca.nome
    equipment_map['maintenance'] = equipment.maintenance

    return equipment_map


def get_equipments(**kwargs):
    """
    Return a list of equipments

    :param user: Id user(optional)
    :param rights_write: Right of Write(optional)
    :param rights_read: Right of Read(optional)
    :param environment: Id of environment(optional)
    :param is_router: Boolean (True|False)(optional)

    """
    eqpts = Equipamento.objects.all()

    if kwargs.get('user', None) is not None:
        q_filter_user = {
            'equipamentogrupo__egrupo__direitosgrupoequipamento'
            '__ugrupo__usuario': kwargs.get('user')
        }
        eqpts = eqpts.filter(Q(**q_filter_user))

    if kwargs.get('rights_write', None) is not None:
        q_filter_rights = {
            'equipamentogrupo__egrupo__direitosgrupoequipamento__escrita': 1
        }
        eqpts = eqpts.filter(Q(**q_filter_rights))

    if kwargs.get('rights_read', None) is not None:
        q_filter_rights = {
            'equipamentogrupo__egrupo__direitosgrupoequipamento__leitura': 1
        }
        eqpts = eqpts.filter(Q(**q_filter_rights))

    if kwargs.get('is_router', None) is not None:
        q_filter_router = {
            'equipamentoambiente__is_router': kwargs.get('is_router')
        }
        eqpts = eqpts.filter(Q(**q_filter_router))

    if kwargs.get('name', None) is not None:
        q_filter_router = {
            'nome': kwargs.get('name')
        }
        eqpts = eqpts.filter(Q(**q_filter_router))

    if kwargs.get('environment', None) is not None:
        q_filters = [{
            'ipequipamento__ip__networkipv4__vlan__ambiente__environmentenvironmentvip'
            '__environment_vip__networkipv4__vlan__ambiente': kwargs.get('environment')
        },
            {
            'ipv6equipament__ip__networkipv6__vlan__ambiente__environmentenvironmentvip'
            '__environment_vip__networkipv6__vlan__ambiente': kwargs.get('environment')
        }]

        eqpts = eqpts.filter(
            reduce(lambda x, y: x | y, [Q(**q_filter) for q_filter in q_filters])
        )

    eqpts = build_query_to_datatable_v3(eqpts, kwargs.get('search', {}))

    return eqpts


def all_equipments_can_update_config(equipment_list, user):

    for equipment in equipment_list:
        q_filter = {
            'equipamentogrupo__egrupo__direitosgrupoequipamento__'
            'ugrupo__usuariogrupo__usuario': user,
            'equipamentogrupo__egrupo__direitosgrupoequipamento__'
            'alterar_config': True,
            'id': equipment.id
        }

        res = Equipamento.objects.filter(
            Q(**q_filter)
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
