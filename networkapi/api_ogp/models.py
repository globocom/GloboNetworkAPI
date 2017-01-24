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
                u'object type not found. pk {}'.format(name))
            raise exceptions.ObjectTypeNotFoundError(name)
        except OperationalError, e:
            cls.log.error(u'Lock wait timeout exceeded.')
            raise OperationalError(
                e, u'Lock wait timeout exceeded; try restarting transaction')
        except Exception, e:
            cls.log.error(u'Failure to search the object type.')
            raise exceptions.ObjectTypeError(
                u'Failure to search the object type.')


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
                u'Failure to search the object group permission.')

    @classmethod
    def get_by_object(cls, object_value, object_type):
        """"Get Object Group Permission General by object_value and object_type.

        @return: Object Group Permission General.

        @raise ObjectGroupPermissionNotFoundError: Object Group Permission
                                                   General not registered.
        @raise ObjectGroupPermissionError: Failed to search for the Object
                                           Group Permission General.
        @raise OperationalError: Lock wait timeout exceeded.
        """
        try:
            return ObjectGroupPermission.objects.filter(
                object_value=object_value,
                object_type__name=object_type)
        except OperationalError, e:
            cls.log.error(u'Lock wait timeout exceeded.')
            raise OperationalError(
                e, u'Lock wait timeout exceeded; try restarting transaction')
        except Exception, e:
            cls.log.error(
                u'Failure to search the object group permission.')
            raise exceptions.ObjectGroupPermissionError(
                u'Failure to search the object group permission.')

    @classmethod
    def get_by_unique_key(cls, user_group, object_type, object_value):
        """"Get Object Group Permission by user_group, object_type and object_value.

        @return: Object Group Permission.

        @raise ObjectGroupPermissionNotFoundError: Object Group Permission
                                                   not registered.
        @raise ObjectGroupPermissionError: Failed to search for the Object
                                           Group Permission.
        @raise OperationalError: Lock wait timeout exceeded.
        """

        try:
            return ObjectGroupPermission.objects.get(
                user_group=user_group,
                object_type__name=object_type,
                object_value=object_value)
        except ObjectDoesNotExist, e:
            cls.log.error(
                u'Object group permission not found. '
                'user_group {}, object_type {}. object_value {}'.format(
                    user_group, object_type, object_value))
            raise exceptions.ObjectGroupPermissionError(
                u'Object group permission general not found. '
                'user_group {}, object_type {}. object_value {}'.format(
                    user_group, object_type, object_value))
        except OperationalError, e:
            cls.log.error(u'Lock wait timeout exceeded.')
            raise OperationalError(
                e, u'Lock wait timeout exceeded; try restarting transaction')
        except Exception, e:
            cls.log.error(
                u'Failure to search the object group permission.')
            raise exceptions.ObjectGroupPermissionError(
                u'Failure to search the object group permission.')

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

    def update_v3(self, perm):

        self.read = perm.get('read')
        self.write = perm.get('write')
        self.change_config = perm.get('change_config')
        self.delete = perm.get('delete')

        self.save()

    def create_perms(self, obj_map, object_value, object_type, user):
        usr_facade = get_app('api_usuario', 'facade')
        usr_models = get_app('usuario', 'models')

        groups_perm = obj_map.get('groups_permissions', [])
        groups_perm += usr_facade.get_groups(
            obj_map.get('users_permissions', []))
        groups_perm = usr_facade.reduce_groups(groups_perm)
        if groups_perm:
            for group_perm in groups_perm:
                perm = {
                    'object_type': object_type,
                    'user_group': group_perm['user_group'],
                    'object_value': object_value,
                    'read': group_perm['read'],
                    'write': group_perm['write'],
                    'delete': group_perm['delete'],
                    'change_config': group_perm['change_config'],
                }
                ogp = ObjectGroupPermission()
                ogp.create_v3(perm)
        else:

            for group in usr_models.UsuarioGrupo.list_by_user_id(user.id):
                perm = {
                    'object_type': object_type,
                    'user_group': group.ugrupo_id,
                    'object_value': object_value,
                    'read': True,
                    'write': True,
                    'delete': True,
                    'change_config': True,
                }

                ogp = ObjectGroupPermission()
                ogp.create_v3(perm)

    def update_perms(self, obj_map, object_value, object_type, user):

        usr_facade = get_app('api_usuario', 'facade')
        usr_models = get_app('usuario', 'models')

        groups_perm = obj_map.get('groups_permissions', [])
        groups_perm += usr_facade.get_groups(
            obj_map.get('users_permissions', []))
        groups_perm = usr_facade.reduce_groups(groups_perm)

        groups_perms_db = ObjectGroupPermission.objects.filter(
            object_type__name=object_type,
            object_value=object_value
        )

        groups_perm_idx = [gp['user_group'] for gp in groups_perm]

        # Empty perms in DB
        if not groups_perms_db:
            for group in usr_models.UsuarioGrupo.list_by_user_id(user.id):
                perm = {
                    'object_type': object_type,
                    'user_group': group.ugrupo_id,
                    'object_value': object_value,
                    'read': True,
                    'write': True,
                    'delete': True,
                    'change_config': True,
                }
                ogp = ObjectGroupPermission()
                ogp.create_v3(perm)
        else:
            for group_perm in groups_perms_db:

                # update perms
                if group_perm.user_group_id in groups_perm_idx:
                    idx = groups_perm_idx.index(group_perm.user_group_id)
                    perm = {
                        'object_type': object_type,
                        'user_group': group_perm.user_group_id,
                        'object_value': object_value,
                        'read': groups_perm[idx]['read'],
                        'write': groups_perm[idx]['write'],
                        'delete': groups_perm[idx]['delete'],
                        'change_config': groups_perm[idx]['change_config'],
                    }
                    ogp = ObjectGroupPermission.get_by_unique_key(
                        user_group=group_perm.user_group_id,
                        object_type=object_type,
                        object_value=object_value)
                    ogp.update_v3(perm)

                # delete perms
                else:
                    ObjectGroupPermission.objects\
                        .filter(id=group_perm.id).delete()
            groups_perms_db_idx = [
                group_perm_db.user_group_id for group_perm_db in groups_perms_db]
            for group_perm in groups_perm:
                # insert perms
                if group_perm['user_group'] not in groups_perms_db_idx:

                    perm = {
                        'object_type': object_type,
                        'user_group': group_perm['user_group'],
                        'object_value': object_value,
                        'read': group_perm['read'],
                        'write': group_perm['write'],
                        'delete': group_perm['delete'],
                        'change_config': group_perm['change_config'],
                    }
                    ogp = ObjectGroupPermission()
                    ogp.create_v3(perm)


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
                u'Failure to search the object group permission general.')

    @classmethod
    def get_by_unique_key(cls, user_group, object_type):
        """"Get Object Group Permission General by user_group and object_type.

        @return: Object Group Permission General.

        @raise ObjectGroupPermissionNotFoundError: Object Group Permission
                                                   General not registered.
        @raise ObjectGroupPermissionError: Failed to search for the Object
                                           Group Permission General.
        @raise OperationalError: Lock wait timeout exceeded.
        """
        try:
            return ObjectGroupPermissionGeneral.objects.get(
                user_group=user_group,
                object_type=object_type)
        except ObjectDoesNotExist, e:
            cls.log.error(
                u'Object group permission general not found. '
                'user_group {}, object_type {}'.format(
                    user_group, object_type))
            raise exceptions.ObjectGroupPermissionGeneralError(
                u'Object group permission general not found. '
                'user_group {}, object_type {}'.format(
                    user_group, object_type))
        except OperationalError, e:
            cls.log.error(u'Lock wait timeout exceeded.')
            raise OperationalError(
                e, u'Lock wait timeout exceeded; try restarting transaction')
        except Exception, e:
            cls.log.error(
                u'Failure to search the object group permission general.')
            raise exceptions.ObjectGroupPermissionGeneralError(
                u'Failure to search the object group permission general.')

    def create_v3(self, perm):

        group_models = get_app('grupo', 'models')

        self.user_group = group_models.UGrupo.get_by_pk(perm.get('user_group'))
        self.object_type = ObjectType.get_by_name(perm.get('object_type'))
        self.read = perm.get('read')
        self.write = perm.get('write')
        self.change_config = perm.get('change_config')
        self.delete = perm.get('delete')

        self.save()

    def update_v3(self, perm):

        self.read = perm.get('read')
        self.write = perm.get('write')
        self.change_config = perm.get('change_config')
        self.delete = perm.get('delete')

        self.save()
