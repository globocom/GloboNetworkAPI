# -*- coding:utf-8 -*-import logging

# from networkapi.admin_permission import AdminPermission
# from networkapi.requisicaovips.models import ServerPool
# from networkapi.api_vip_request.models import VipRequest

# log = logging.getLogger(__name__)


# def validate_pool_perm(pools, user, pool_operation):

#     if len(pools) == 0:
#         return False

#     server_pools = ServerPool.objects.filter(id__in=pools)
#     for pool in server_pools:

#         perms = pool.serverpoolgrouppermission_set.all()

#         if not perms:
#             return True

#         ugroups = user.grupos.all()

#         if perms:

#             pool_perm = validate_obj(perms, ugroups, pool_operation)
#             if not pool_perm:
#                 log.warning('User{} does not have permission to Pool {}'.format(
#                     user, pool.id
#                 ))
#                 return False

#     return True


# def validate_vip_perm(vips, user, vip_operation):

#     if len(vips) == 0:
#         return False

#     vips_request = VipRequest.objects.filter(id__in=vips)
#     for vip in vips_request:

#         perms = vip.viprequestgrouppermission_set.all()

#         if not perms:
#             return True

#         ugroups = user.grupos.all()

#         if perms:

#             vip_perm = validate_obj(perms, ugroups, vip_operation)
#             if not vip_perm:
#                 log.warning('User{} does not have permission to Vip {}'.format(
#                     user, vip.id
#                 ))
#                 return False

#     return True


# def validate_obj(perms, ugroups, pool_operation):
#     obj_perm = False
#     for perm in perms:

#         perm = perm.filter(user_group__in=ugroups)

#         if pool_operation == AdminPermission.POOL_READ_OPERATION:
#             perm = perm.filter(read=True)
#         elif pool_operation == AdminPermission.POOL_WRITE_OPERATION:
#             perm = perm.filter(write=True)
#         elif pool_operation == AdminPermission.POOL_DELETE_OPERATION:
#             perm = perm.filter(delete=True)
#         elif pool_operation == AdminPermission.POOL_UPDATE_CONFIG_OPERATION:
#             perm = perm.filter(change_config=True)

#         if perm:
#             obj_perm = True
#             break

#     return obj_perm
