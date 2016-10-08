# -*- coding: utf-8 -*-
import logging

from networkapi.usuario.models import UsuarioGrupo
# from networkapi.admin_permission import AdminPermission


log = logging.getLogger(__name__)


def get_groups(users_permissions):
    groups = list()
    for user_permission in users_permissions:
        for group in UsuarioGrupo.list_by_user_id(user_permission['user']):
            group_id = int(group.ugrupo.id)
            if group_id != 1:
                groups.append({
                    'group': group_id,
                    'read': user_permission['read'],
                    'write': user_permission['write'],
                    'delete': user_permission['delete'],
                    'change_config': user_permission['change_config'],
                })
    return groups


def reduce_groups(groups):
    group_reduce = list()
    group_reduce_idx = list()
    for group in groups:
        if group['group'] in group_reduce_idx:
            idx = group_reduce_idx[group['group']]
            if group['read']:
                group_reduce[idx]['read']
            if group['write']:
                group_reduce[idx]['write']
            if group['delete']:
                group_reduce[idx]['delete']
            if group['change_config']:
                group_reduce[idx]['change_config']
        else:
            group_reduce_idx.append(group['group'])
            group_reduce.append(group)
    return group_reduce
