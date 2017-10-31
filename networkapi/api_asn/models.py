# -*- coding: utf-8 -*-
import logging

from _mysql_exceptions import OperationalError
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models import get_model

from networkapi.api_asn.v4 import exceptions
from networkapi.models.BaseModel import BaseModel


class Asn(BaseModel):

    id = models.AutoField(
        primary_key=True,
        db_column='id'
    )

    name = models.CharField(
        blank=False,
        max_length=45
    )

    description = models.CharField(
        blank=True,
        null=False,
        max_length=200
    )

    def _get_equipments(self):
        return self.asnequipment_set.all()

    equipments = property(_get_equipments)

    log = logging.getLogger('Asn')

    class Meta(BaseModel.Meta):
        db_table = u'asn'
        managed = True

    @classmethod
    def get_by_pk(cls, id):
        """Get AS by id.

        :return: AS.

        :raise AsnNotFoundError: As not registered.
        :raise AsnError: Failed to search for the As.
        :raise OperationalError: Lock wait timeout exceeded
        """
        try:
            return Asn.objects.get(id=id)
        except ObjectDoesNotExist, e:
            cls.log.error(u'ASN not found. pk {}'.format(id))
            raise exceptions.AsnNotFoundError(id)
        except OperationalError, e:
            cls.log.error(u'Lock wait timeout exceeded.')
            raise OperationalError(
                e, u'Lock wait timeout exceeded; try restarting transaction')
        except Exception, e:
            cls.log.error(u'Failure to search the ASN.')
            raise exceptions.AsnError(
                e, u'Failure to search the ASN.')

    def create_v4(self, as_map):
        """Create ASN."""

        self.name = as_map.get('name')
        self.description = as_map.get('description')

        self.save()

    def update_v4(self, as_map):
        """Update ASN."""

        self.name = as_map.get('name')
        self.description = as_map.get('description')

        self.save()

    def delete_v4(self):
        """Delete ASN.

        :raise AsnAssociatedToEquipmentError: ASN cannot be deleted because it
                                             is associated to at least one
                                             equipment.
        """
        try:

            if self.asnequipment_set.count() > 0:
                ids_equipments = [asnequipment.equipment_id
                                  for asnequipment
                                  in self.asnequipment_set.all()]

                ids_equipments = map(int, ids_equipments)
                msg = u'Cannot delete ASN {} because it is associated ' \
                      u'with Equipments {}.'.\
                    format(self.id, ids_equipments)
                raise exceptions.AsnAssociatedToEquipmentError(
                    msg
                )

            super(Asn, self).delete()

        except exceptions.AsnAssociatedToEquipmentError, e:
            self.log.error(e)
            raise exceptions.AsnAssociatedToEquipmentError(e.detail)
        except Exception, e:
            self.log.error(e)
            raise exceptions.AsnErrorV4(e)


class AsnEquipment(BaseModel):
    id = models.AutoField(primary_key=True, db_column='id')

    asn = models.ForeignKey(
        'api_asn.Asn',
        db_column='id_asn',
        blank=True,
        null=True
    )

    equipment = models.ForeignKey(
        'equipamento.Equipamento',
        db_column='id_equipment',
        blank=True,
        null=True
    )

    log = logging.getLogger('AsnEquipment')

    class Meta(BaseModel.Meta):
        db_table = u'asn_equipment'
        managed = True

    @classmethod
    def get_by_pk(cls, id):
        """Get AsnEquipment by id.

        :return: AsnEquipment.

        :raise AsnEquipmentNotFoundError: AsnEquipment not registered.
        :raise AsnEquipmentError: Failed to search for the AsnEquipment.
        :raise OperationalError: Lock wait timeout exceeded
        """
        try:
            return AsnEquipment.objects.get(id=id)
        except ObjectDoesNotExist, e:
            cls.log.error(u'AsnEquipment not found. pk {}'.format(id))
            raise exceptions.AsnEquipmentNotFoundError(id)
        except OperationalError, e:
            cls.log.error(u'Lock wait timeout exceeded.')
            raise OperationalError(
                e, u'Lock wait timeout exceeded; try restarting transaction')
        except Exception, e:
            cls.log.error(u'Failure to search the AS.')
            raise exceptions.AsnEquipmentError(
                e, u'Failure to search the AS.')

    def create_v4(self, as_equipment):
        """Create AsnEquipment relationship."""

        equipment = get_model('equipamento', 'Equipamento')

        self.equipment = equipment().get_by_pk(
            as_equipment.get('equipment'))
        self.asn = Asn().get_by_pk(as_equipment.get('asn'))

        self.save()

    def delete_v4(self):
        """Delete AsnEquipment relationship."""

        super(AsnEquipment, self).delete()

