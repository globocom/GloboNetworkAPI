# -*- coding: utf-8 -*-
import logging

from _mysql_exceptions import OperationalError
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models import get_model

from networkapi.api_virtual_interface.v4 import exceptions
from networkapi.models.BaseModel import BaseModel



class VirtualInterface(BaseModel):
    id = models.AutoField(primary_key=True, db_column='id')
    name = models.CharField(blank=False, max_length=45)

    vrf = models.ForeignKey(
        'api_vrf.Vrf',
        db_column='id_vrf',
        null=True
    )

    log = logging.getLogger('VirtualInterface')

    class Meta(BaseModel.Meta):
        db_table = u'virtual_interface'
        managed = True


    def _get_ipv4_equipment_virtual_interface(self):

        return self.ipequipamento_set.all()

    ipv4_equipment_virtual_interface = \
        property(_get_ipv4_equipment_virtual_interface)

    def _get_ipv6_equipment_virtual_interface(self):

        return self.ipv6equipament_set.all()

    ipv6_equipment_virtual_interface = \
        property(_get_ipv6_equipment_virtual_interface)

    @classmethod
    def get_by_pk(cls, id):
        """Get Virtual Interface by id.

        :return: Virtual Interface.

        :raise VirtualInterfaceNotFoundError: Virtual Interface not registered.
        :raise VirtualInterfaceError: Failed to search for the Virtual Interface.
        :raise OperationalError: Lock wait timeout exceeded
        """
        try:
            return VirtualInterface.objects.get(id=id)
        except ObjectDoesNotExist, e:
            cls.log.error(u'Virtual Interface not found. pk {}'.format(id))
            raise exceptions.VirtualInterfaceNotFoundError(id)
        except OperationalError, e:
            cls.log.error(u'Lock wait timeout exceeded.')
            raise OperationalError(
                e, u'Lock wait timeout exceeded; try restarting transaction')
        except Exception, e:
            cls.log.error(u'Failure to search the Virtual Interface.')
            raise exceptions.VirtualInterfaceError(
                e, u'Failure to search the Virtual Interface.')

    def create_v4(self, vi_map):
        """Create Virtual Interface."""

        vrf_model = get_model('api_vrf', 'Vrf')

        self.name = vi_map.get('name')
        self.vrf = vrf_model().get_by_pk(vi_map.get('vrf'))

        self.save()

    def update_v4(self, vi_map):
        """Update Virtual Interface."""

        vrf_model = get_model('api_vrf', 'Vrf')

        self.name = vi_map.get('name')
        self.vrf = vrf_model().get_by_pk(vi_map.get('vrf'))

        self.save()

    def delete_v4(self):
        """Delete Virtual Interface.

        """
        try:

            # Cascade delete related Neighbors
            for neighbor in self.neighbor_set.all():
                neighbor.delete()

            for ipeqpt in self.ipequipamento_set.all():
                ipeqpt.update_v4(None)

            for ipv6eqpt in self.ipv6equipament_set.all():
                ipv6eqpt.update_v4(None)

            super(VirtualInterface, self).delete()

        except Exception, e:
            self.log.error(e)
            raise exceptions.VirtualInterfaceErrorV4(e)