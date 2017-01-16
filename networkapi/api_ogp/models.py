# -*- coding: utf-8 -*-
import logging

from _mysql_exceptions import OperationalError
from django.core.exceptions import ObjectDoesNotExist
from django.db import models

from networkapi.api_ogp import exceptions
from networkapi.models.BaseModel import BaseModel
from networkapi.util.geral import get_app


class ObjectType(BaseModel):
    id = models.AutoField(primary_key=True, db_column='id')
    name = models.CharField(
        max_length=45,
        db_column='name'
    )

    log = logging.getLogger('ObjectType')

    class Meta(BaseModel.Meta):
        db_table = u'object_type'
        managed = True

    @classmethod
    def get_by_name(cls, name):
        """"
        Get Object Type by id.

        @return: Object Type.

        @raise ObjectTypeNotFoundError: Object Type not registered.
        @raise ObjectTypeError: Failed to search for the Object Type.
        @raise OperationalError: Lock wait timeout exceeded.
        """
        try:
            return ObjectType.objects.get(name=name)
        except ObjectDoesNotExist, e:
            cls.log.error(
                u'object type not found. pk {}'.format(id))
            raise exceptions.ObjectTypeNotFoundError(id)
        except OperationalError, e:
            cls.log.error(u'Lock wait timeout exceeded.')
            raise OperationalError(
                e, u'Lock wait timeout exceeded; try restarting transaction')
        except Exception, e:
            cls.log.error(u'Failure to search the object type.')
            raise exceptions.ObjectTypeError(
                e, u'Failure to search the object type.')


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

    log = logging.getLogger('ObjectGroupPermission')

    class Meta(BaseModel.Meta):
        db_table = u'object_group_permission'
        managed = True
        unique_together = ('user_group', 'object_type', 'object_value')

    @classmethod
    def get_by_pk(cls, id):
        """"
        Get Object Group Permission by id.

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

    def create_v3(self, perm):

        group_models = get_app('grupo', 'models')

        self.user_group = group_models.UGrupo.get_by_pk(perm.get('user_group'))
        self.object_type = ObjectType.get_by_name(perm.get('object_type'))
        self.object_value = perm.get('object_value')
        self.read = perm.get('read')
        self.write = perm.get('write')
        self.change_config = perm.get('change_config')
        self.delete = perm.get('delete')

        self.save()


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

    log = logging.getLogger('ObjectGroupPermissionGeneral')

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

    def create_v3(self, perm):

        group_models = get_app('grupo', 'models')

        self.user_group = group_models.UGrupo.get_by_pk(perm.get('user_group'))
        self.object_type = ObjectType.get_by_name(perm.get('object_type'))
        self.object_value = perm.get('object_value')
        self.read = perm.get('read')
        self.write = perm.get('write')
        self.change_config = perm.get('change_config')
        self.delete = perm.get('delete')

        self.save()
