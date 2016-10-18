# -*- coding: utf-8 -*-
from _mysql_exceptions import OperationalError
from django.core.exceptions import ObjectDoesNotExist
from django.db import models

from networkapi.api_ogp import exceptions
from networkapi.models.BaseModel import BaseModel


class ObjectType(BaseModel):
    id = models.AutoField(primary_key=True, db_column='id')
    name = models.CharField(
        max_length=45,
        db_column='name'
    )

    class Meta(BaseModel.Meta):
        db_table = u'object_type'
        managed = True


class ObjectGroupPermission(BaseModel):
    id = models.AutoField(primary_key=True, db_column='id')
    user_group = models.ForeignKey(
        'grupo.UGrupo',
        db_column='id_user_group'
    )
    object_type = models.ForeignKey(ObjectType, db_column='id_object_type')
    object_value = models.IntegerField(db_column='id_object')
    read = models.BooleanField()
    write = models.BooleanField()
    change_config = models.BooleanField()
    delete = models.BooleanField()

    class Meta(BaseModel.Meta):
        db_table = u'object_group_permission'
        managed = True
        unique_together = ('user_group', 'object_type', 'object_value')

    @classmethod
    def get_by_pk(cls, id):
        """"Get Object Group Permission by id.

        @return: Object Group Permission.

        @raise ObjectGroupPermissionNotFoundError: Object Group Permission
                                                   not registered.
        @raise ObjectGroupPermissionError: Failed to search for the Object
                                           Group Permission.
        @raise OperationalError: Lock wait timeout exceeded.
        """
        try:
            return ObjectGroupPermission.objects.get(id=id)
        except ObjectDoesNotExist, e:
            cls.log.error(
                u'object group permission not found. pk {}'.format(id))
            raise exceptions.ObjectGroupPermissionNotFoundError(id)
        except OperationalError, e:
            cls.log.error(u'Lock wait timeout exceeded.')
            raise OperationalError(
                e, u'Lock wait timeout exceeded; try restarting transaction')
        except Exception, e:
            cls.log.error(u'Failure to search the object group permission.')
            raise exceptions.ObjectGroupPermissionError(
                e, u'Failure to search the object group permission.')


class ObjectGroupPermissionGeneral(BaseModel):
    id = models.AutoField(primary_key=True, db_column='id')
    user_group = models.ForeignKey(
        'grupo.UGrupo',
        db_column='id_user_group'
    )
    object_type = models.ForeignKey(ObjectType, db_column='id_object_type')
    read = models.BooleanField()
    write = models.BooleanField()
    change_config = models.BooleanField()
    delete = models.BooleanField()

    class Meta(BaseModel.Meta):
        db_table = u'object_group_permission_general'
        managed = True
        unique_together = ('user_group', 'object_type')

    @classmethod
    def get_by_pk(cls, id):
        """"Get Object Group Permission General by id.

        @return: Object Group Permission General.

        @raise ObjectGroupPermissionNotFoundError: Object Group Permission
                                                   General not registered.
        @raise ObjectGroupPermissionError: Failed to search for the Object
                                           Group Permission General.
        @raise OperationalError: Lock wait timeout exceeded.
        """
        try:
            return ObjectGroupPermissionGeneral.objects.get(id=id)
        except ObjectDoesNotExist, e:
            cls.log.error(
                u'object group permission general not found. pk {}'.format(id))
            raise exceptions.ObjectGroupPermissionGeneralNotFoundError(id)
        except OperationalError, e:
            cls.log.error(u'Lock wait timeout exceeded.')
            raise OperationalError(
                e, u'Lock wait timeout exceeded; try restarting transaction')
        except Exception, e:
            cls.log.error(
                u'Failure to search the object group permission general.')
            raise exceptions.ObjectGroupPermissionGeneralError(
                e, u'Failure to search the object group permission general.')
