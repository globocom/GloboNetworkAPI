import logging

from networkapi.admin_permission import AdminPermission
from networkapi.api_ogp import models
log = logging.getLogger(__name__)


def validate_object_perm(objects_id, user, operation, object_type):

    if len(objects_id) == 0:
        return False

    for object_id in objects_id:

        ugroups = user.grupos.all()

        # general perms
        perms = models.ObjectGroupPermissionGeneral.objects.filter(
            object_type__name=object_type
        )
        if perms:
            pool_perm = _validate_obj(perms, ugroups, operation)
            if pool_perm:
                return True

        # individuals perms
        perms = models.ObjectGroupPermission.objects.filter(
            object_value=object_id,
            object_type__name=object_type
        )
        if perms:
            pool_perm = _validate_obj(perms, ugroups, operation)
            if not pool_perm:
                log.warning('User{} does not have permission {} to Object {}:{}'.format(
                    user, operation, object_type, object_id
                ))
                return False

    return True


def _validate_obj(perms, ugroups, operation):
    obj_perm = False

    perms = perms.filter(user_group__in=ugroups)

    if operation == AdminPermission.OBJ_READ_OPERATION:
        perms = perms.filter(read=True)
    elif operation == AdminPermission.OBJ_WRITE_OPERATION:
        perms = perms.filter(write=True)
    elif operation == AdminPermission.OBJ_DELETE_OPERATION:
        perms = perms.filter(delete=True)
    elif operation == AdminPermission.OBJ_UPDATE_CONFIG_OPERATION:
        perms = perms.filter(change_config=True)

    if perms:
        obj_perm = True

    return obj_perm


def perm_obj(request, operation, object_type, *args, **kwargs):

    objs = kwargs.get('obj_ids').split(';')
    return validate_object_perm(
        objs,
        request.user,
        operation,
        object_type
    )
