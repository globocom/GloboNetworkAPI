# -*- coding: utf-8 -*-
import logging

from django.core.exceptions import FieldError
from django.db.models import Q
from networkapi.api_equipment.facade import get_equipment_by_id

from networkapi.api_equipment.exceptions import EquipmentInvalidValueException
from networkapi.api_equipment.v4 import exceptions
from networkapi.api_rest.exceptions import NetworkAPIException
from networkapi.api_rest.exceptions import ObjectDoesNotExistException
from networkapi.api_rest.exceptions import ValidationAPIException
from networkapi.distributedlock import LOCK_EQUIPMENT
from networkapi.equipamento.models import Equipamento
from networkapi.equipamento.models import EquipamentoAmbiente
from networkapi.equipamento.models import EquipamentoError
from networkapi.equipamento.models import EquipamentoNotFoundError
from networkapi.infrastructure.datatable import build_query_to_datatable_v3
from networkapi.plugins.base import BasePlugin
from networkapi.plugins.factory import PluginFactory
from networkapi.util.geral import create_lock
from networkapi.util.geral import destroy_lock

log = logging.getLogger(__name__)

def update_equipment(equipments, user):
    """Update equipment."""

    locks_list = create_lock(equipments, LOCK_EQUIPMENT)
    response = list()

    try:
        for equipment in equipments:
            equipment_obj = get_equipment_by_id(equipment.get('id'))
            equipment_obj.update_v4(equipment)
            response.append({'id': equipment_obj.id})
    except ObjectDoesNotExistException, e:
        raise ObjectDoesNotExistException(e.detail)
    except EquipamentoError, e:
        raise ValidationAPIException(e.message)
    except EquipmentInvalidValueException, e:
        raise ValidationAPIException(str(e))
    except ValidationAPIException, e:
        raise ValidationAPIException(str(e))
    except Exception, e:
        raise NetworkAPIException(str(e))
    finally:
        destroy_lock(locks_list)

    return response


def create_equipment(equipments, user):
    """Create equipment"""

    response = list()

    try:
        for equipment in equipments:
            equipment_obj = Equipamento()
            equipment_obj.create_v4(equipment)
            response.append({'id': equipment_obj.id})
    except EquipamentoError, e:
        raise ValidationAPIException(e.message)
    except EquipmentInvalidValueException, e:
        raise ValidationAPIException(e.detail)
    except ValidationAPIException, e:
        raise ValidationAPIException(e.detail)
    except Exception, e:
        raise NetworkAPIException(str(e))

    return response


def delete_equipment(equipments):
    """Delete equipment by ids"""

    locks_list = create_lock(equipments, LOCK_EQUIPMENT)

    try:
        for equipment in equipments:
            equipment_obj = get_equipment_by_id(equipment)
            equipment_obj.delete_v4()
    except ObjectDoesNotExistException, e:
        raise ObjectDoesNotExistException(e.detail)
    except EquipamentoError, e:
        raise ValidationAPIException(e.message)
    except EquipmentInvalidValueException, e:
        raise ValidationAPIException(e.detail)
    except ValidationAPIException, e:
        raise ValidationAPIException(e.detail)
    except Exception, e:
        raise NetworkAPIException(str(e))
    finally:
        destroy_lock(locks_list)



def get_equipment_port_channel(equipment_id, channel_number):
    """Get information of a port-channel from the equipment itself.

    :param equipment_id: Id of equipment.
    :param channel_number: Number of port-channel, e.g. 1. Each plugin
        converts it to the name used by the equipment (e.g. ae1).
    """

    equipment = get_equipment_by_id(equipment_id)

    try:
        plugin = PluginFactory.factory(equipment)
    except NotImplementedError:
        raise exceptions.PortChannelNotSupportedException(equipment.nome)

    # Factory returns a message instead of plugin when there is no access
    if not isinstance(plugin, BasePlugin):
        raise exceptions.EquipmentWithoutAccessException(equipment.nome)

    # Temporarily allow connecting to equipments even if the plugin does not explicitly implement get_port_channel
    # # Avoid connecting to equipments whose plugin does not implement it
    # if type(plugin).get_port_channel.im_func is \
    #         BasePlugin.get_port_channel.im_func:
    #     raise exceptions.PortChannelNotSupportedException(equipment.nome)

    plugin.connect()
    port_channel = plugin.get_port_channel(channel_number)
    plugin.close()

    return port_channel
