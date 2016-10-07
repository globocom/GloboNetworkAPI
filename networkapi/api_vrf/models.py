import logging

from django.db import models

from networkapi.equipamento.models import Equipamento
from networkapi.models.BaseModel import BaseModel
from networkapi.vlan.models import Vlan


class Vrf(BaseModel):

    id = models.AutoField(
        primary_key=True,
        db_column='id_rule'
    )
    vrf = models.TextField(
        max_length=45,
        db_column='vrf'
    )

    log = logging.getLogger('Vrf')

    class Meta (BaseModel.Meta):
        managed = True
        db_table = u'vrf'


class VrfVlanEquipment(BaseModel):

    id = models.AutoField(
        primary_key=True,
        db_column='id'
    )
    vrf = models.ForeignKey(
        Vrf,
        db_column='id_vrf',
        null=False
    )
    vlan = models.ForeignKey(
        Vlan,
        db_column='id_vlan',
        null=False
    )
    equipment = models.ForeignKey(
        Equipamento,
        db_column='id_equipment',
        null=False
    )

    log = logging.getLogger('VrfVlanEquipment')

    class Meta (BaseModel.Meta):
        db_table = u'vrf_vlan_equipment'
        managed = True
