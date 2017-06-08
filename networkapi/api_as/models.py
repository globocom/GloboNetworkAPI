# -*- coding: utf-8 -*-
import logging

from django.db import models

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

    log = logging.getLogger('As')

    class Meta(BaseModel.Meta):
        db_table = u'as'
        managed = True

    @classmethod
    def get_by_pk(cls):
        pass

    def create_v3(self):
        pass

    def update_v3(self):
        pass

    def delete_v3(self):
        pass


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
        pass

    def create_v3(self):
        pass

    def update_v3(self):
        pass

    def delete_v3(self):
        pass
