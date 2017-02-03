# -*- coding: utf-8 -*-
import logging

from django.db.models import Q

from networkapi.api_rest.exceptions import NetworkAPIException
from networkapi.api_rest.exceptions import ObjectDoesNotExistException
from networkapi.api_rest.exceptions import ValidationAPIException
from networkapi.equipamento.models import Equipamento
from networkapi.equipamento.models import EquipamentoAmbiente
from networkapi.equipamento.models import EquipamentoNotFoundError
from networkapi.infrastructure.datatable import build_query_to_datatable_v3


log = logging.getLogger(__name__)


def get_equipment_by_id(equipment_id):
    """Get equipment by id"""

    try:
        equipment = Equipamento().get_by_pk(equipment_id)
    except EquipamentoNotFoundError, e:
        raise ObjectDoesNotExistException(str(e))
    except Exception, e:
        raise NetworkAPIException(str(e))
    else:
        return equipment


def get_equipment_by_ids(equipment_ids):
    """Get equipment by ids"""

    eqpt_ids = list()
    for equipment_id in equipment_ids:
        try:
            equipment = get_equipment_by_id(equipment_id)
        except ObjectDoesNotExistException, e:
            raise ObjectDoesNotExistException(str(e))
        except Exception, e:
            raise NetworkAPIException(str(e))
        else:
            eqpt_ids.append(equipment.id)

    equipments = Equipamento.objects.filter(id__in=eqpt_ids)

    return equipments


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
    equipment_map[
        'tipo_equipamento'] = equipment.tipo_equipamento.tipo_equipamento
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
            reduce(lambda x, y: x | y, [Q(**q_filter)
                                        for q_filter in q_filters])
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


def update_equipment(equipment, user):
    """Update equipment"""
    try:
        equipment_obj = get_equipment_by_id(equipment.get('id'))
    except ObjectDoesNotExistException, e:
        raise ObjectDoesNotExistException(str(e))
    except Exception, e:
        raise NetworkAPIException(str(e))
    else:
        equipment_obj.update_v3(equipment)

    return equipment_obj


def create_equipment(equipment, user):
    """Create equipment"""

    try:
        equipment_obj = Equipamento()
        equipment_obj.create_v3(equipment)
    except ValidationAPIException, e:
        raise ValidationAPIException(str(e))
    except Exception, e:
        raise NetworkAPIException(str(e))

    return equipment_obj


def delete_equipment(equipments):
    """Delete equipment by ids"""

    for equipment in equipments:
        try:
            equipment_obj = get_equipment_by_id(equipment)
        except ObjectDoesNotExistException, e:
            raise ObjectDoesNotExistException(str(e))
        except Exception, e:
            raise NetworkAPIException(str(e))
        else:
            equipment_obj.delete_v3()


def get_eqpt_by_envvip(environmentvip):
    """Get equipments by environment vip"""

    equips = Equipamento.objects.filter(
        equipamentoambiente__ambiente__vlan__networkipv4__ambient_vip__id=environmentvip,
        maintenance=0,
        tipo_equipamento__tipo_equipamento=u'Balanceador'
    ).distinct()

    # does not implemented yet
    # equips = Equipamento.objects.filter(
    #     equipamentoambiente__ambiente__vlan__networkipv6__ambient_vip__id=vip_request['environmentvip'],
    #     maintenance=0,
    #     tipo_equipamento__tipo_equipamento=u'Balanceador').distinct()

    return equips
