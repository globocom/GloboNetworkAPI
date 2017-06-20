# -*- coding: utf-8 -*-
import logging

from _mysql_exceptions import OperationalError
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models import get_model

from networkapi.api_as.v4 import exceptions
from networkapi.models.BaseModel import BaseModel


class As(BaseModel):

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

    def _get_equipment(self):
        equipment = self.asequipment_set.all()
        if equipment:
            return equipment[0].equipment
        return None

    equipment = property(_get_equipment)

    def _get_equipment_id(self):
        equipment = self.asequipment_set.all()
        if equipment:
            return equipment[0].equipment.id
        return None

    equipment_id = property(_get_equipment_id)

    log = logging.getLogger('As')

    class Meta(BaseModel.Meta):
        db_table = u'as'
        managed = True

    @classmethod
    def get_by_pk(cls, id):
        """Get AS by id.

        :return: AS.

        :raise AsNotFoundError: As not registered.
        :raise AsError: Failed to search for the As.
        :raise OperationalError: Lock wait timeout exceeded
        """
        try:
            return As.objects.get(id=id)
        except ObjectDoesNotExist, e:
            cls.log.error(u'AS not found. pk {}'.format(id))
            raise exceptions.AsNotFoundError(id)
        except OperationalError, e:
            cls.log.error(u'Lock wait timeout exceeded.')
            raise OperationalError(
                e, u'Lock wait timeout exceeded; try restarting transaction')
        except Exception, e:
            cls.log.error(u'Failure to search the AS.')
            raise exceptions.AsError(
                e, u'Failure to search the AS.')

    def create_v4(self, as_map):
        """Create AS."""

        self.name = as_map.get('name')
        self.description = as_map.get('description')

        self.save()

    def update_v4(self, as_map):
        """Update AS."""

        self.name = as_map.get('name')
        self.description = as_map.get('description')

        self.save()

    def delete_v4(self):
        """Delete AS.

        :raise ASAssociatedToEquipmentError: AS cannot be deleted because it
                                             is associated to at least one
                                             equipment.
        """
        try:

            if self.asequipment_set.count() > 0:
                id_equipment = self.asequipment_set.all()[0].equipment_id
                msg = u'Cannot delete AS {} because it is associated ' \
                      u'with Equipment {}.'.\
                    format(self.id, id_equipment)
                raise exceptions.AsAssociatedToEquipmentError(
                    msg
                )

            super(As, self).delete()

        except exceptions.AsAssociatedToEquipmentError, e:
            self.log.error(e)
            raise exceptions.AsAssociatedToEquipmentError(e.detail)
        except Exception, e:
            self.log.error(e)
            raise exceptions.AsErrorV4(e)


class AsEquipment(BaseModel):
    id = models.AutoField(primary_key=True, db_column='id')

    id_as = models.ForeignKey(
        As,
        db_column='id_as',
        blank=True,
        null=True
    )

    equipment = models.ForeignKey(
        'equipamento.Equipamento',
        db_column='id_equipment',
        blank=True,
        null=True
    )

    log = logging.getLogger('AsEquipment')

    class Meta(BaseModel.Meta):
        db_table = u'as_equipment'
        managed = True

    @classmethod
    def get_by_pk(cls):
        """Get AsEquipment by id.

        :return: AsEquipment.

        :raise AsEquipmentNotFoundError: AsEquipment not registered.
        :raise AsEquipmentError: Failed to search for the AsEquipment.
        :raise OperationalError: Lock wait timeout exceeded
        """
        try:
            return AsEquipment.objects.get(id=id)
        except ObjectDoesNotExist, e:
            cls.log.error(u'AsEquipment not found. pk {}'.format(id))
            raise exceptions.AsEquipmentNotFoundError(id)
        except OperationalError, e:
            cls.log.error(u'Lock wait timeout exceeded.')
            raise OperationalError(
                e, u'Lock wait timeout exceeded; try restarting transaction')
        except Exception, e:
            cls.log.error(u'Failure to search the AS.')
            raise exceptions.AsEquipmentError(
                e, u'Failure to search the AS.')

    def create_v4(self, as_equipment):
        """Create AsEquipment relationship."""

        equipment = get_model('equipamento', 'Equipamento')

        self.equipment = equipment().get_by_pk(
            as_equipment.get('equipment'))
        self.id_as = As().get_by_pk(as_equipment.get('id_as'))

        self.save()

    def delete_v4(self):
        """Delete AsEquipment relationship."""

        super(AsEquipment, self).delete()

