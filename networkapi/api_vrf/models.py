# -*- coding: utf-8 -*-
import logging

from _mysql_exceptions import OperationalError
from django.core.exceptions import ObjectDoesNotExist
from django.db import models

from networkapi.api_vrf.exceptions import VrfError
from networkapi.api_vrf.exceptions import VrfNotFoundError
from networkapi.models.BaseModel import BaseModel


class Vrf(BaseModel):

    id = models.AutoField(
        primary_key=True,
        db_column='id'
    )
    vrf = models.TextField(
        max_length=45,
        db_column='vrf'
    )
    internal_name = models.TextField(
        max_length=45,
        db_column='internal_name'
    )

    log = logging.getLogger('Vrf')

    @classmethod
    def get_by_pk(cls, id_vlan):
        """Get Vrf by id.

        @return: Vrf.

        @raise VrfNotFoundError: Vrf is not registered.
        @raise VrfError: Failed to search for the Vrf.
        @raise OperationalError: Lock wait timeout exceed
        """
        try:
            return Vrf.objects.filter(id=id_vlan).uniqueResult()
        except ObjectDoesNotExist, e:
            raise VrfNotFoundError(
                e, u'Dont there is a Vrf by pk = %s.' % id_vlan)
        except OperationalError, e:
            cls.log.error(u'Lock wait timeout exceeded.')
            raise OperationalError(
                e, u'Lock wait timeout exceeded; try restarting transaction')
        except Exception, e:
            cls.log.error(u'Failure to search the Vrf.')
            raise VrfError(e, u'Failure to search the Vrf.')

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
        'vlan.Vlan',
        db_column='id_vlan',
        null=False
    )
    equipment = models.ForeignKey(
        'equipamento.Equipamento',
        db_column='id_equipment',
        null=False
    )

    log = logging.getLogger('VrfVlanEquipment')

    class Meta (BaseModel.Meta):
        db_table = u'vrf_vlan_eqpt'
        managed = True
        unique_together = ('vlan', 'equipment')


class VrfEquipment(BaseModel):

    id = models.AutoField(
        primary_key=True,
        db_column='id'
    )
    vrf = models.ForeignKey(
        'api_vrf.Vrf',
        db_column='id_vrf',
        null=False
    )
    equipment = models.ForeignKey(
        'equipamento.Equipamento',
        db_column='id_equipment',
        null=False
    )
    internal_name = models.TextField(
        max_length=45,
        db_column='internal_name'
    )

    log = logging.getLogger('VrfVlanEquipment')

    class Meta (BaseModel.Meta):
        db_table = u'vrf_eqpt'
        managed = True
        unique_together = ('vrf', 'equipment')
