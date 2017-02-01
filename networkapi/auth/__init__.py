# -*- coding: utf-8 -*-
# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import logging

from networkapi.admin_permission import AdminPermission
from networkapi.api_ogp import models
from networkapi.equipamento.models import Equipamento
from networkapi.grupo.models import DireitosGrupoEquipamento
from networkapi.grupo.models import EGrupo
from networkapi.grupo.models import PermissaoAdministrativa
from networkapi.grupo.models import PermissaoAdministrativaNotFoundError
from networkapi.usuario.models import Usuario

log = logging.getLogger(__name__)


def authenticate(username, password, user_ldap=None):
    """
    Busca o usuário com ativo com o login e senha informados.

    @raise UsuarioError: Falha ao pesquisar o usuário.
    """
    if username is None or password is None:
        return None

    if user_ldap is None:
        return Usuario().get_enabled_user(username, password)
    else:
        return Usuario().get_by_ldap_user(user_ldap, True)


def has_perm(user, perm_function, perm_oper, egroup_id=None, equip_id=None, equip_oper=None):
    """
    @raise EGrupoNotFoundError: Grupo do equipamento nao cadastrado.

    @raise EquipamentoNotFoundError: Equipamento nao cadastrado.

    @raise GrupoError: Falha ao pesquisar os direitos do grupo-equipamento, ou as permissões administrativas, ou o grupo do equipamento.

    @raise EquipamentoError: Falha ao pesquisar o equipamento.
    """
    if user is None:
        return False

    egroups = None
    if egroup_id is not None:
        egroup = EGrupo.get_by_pk(egroup_id)
        egroups = [egroup]
    elif equip_id is not None:
        equip = Equipamento.get_by_pk(equip_id, 'grupos')
        egroups = equip.grupos.all()
        if len(egroups) == 0:
            return False

    ugroups = user.grupos.all()
    for ugroup in ugroups:
        try:
            # perm = PermissaoAdministrativa().get_permission(perm_function, ugroup, perm_oper)
            PermissaoAdministrativa().get_permission(perm_function, ugroup, perm_oper)
            if (egroups is None) or (_has_equip_perm(ugroup, egroups, equip_oper)):
                return True
        except PermissaoAdministrativaNotFoundError:
            continue
    return False


def _has_equip_perm(ugroup, egroups, equip_oper):
    if len(egroups) == 0:
        return False

    direitos = DireitosGrupoEquipamento.search(ugroup.id, equip_oper)
    for direito in direitos:
        if direito.egrupo in egroups:
            return True
    return False


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
                log.warning('User {} does not have permission {} to Object {}:{}'.format(
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

    obj_ids = kwargs.get('obj_ids')
    objs = obj_ids.split(';') if obj_ids is not None else []

    return validate_object_perm(
        objs,
        request.user,
        operation,
        object_type
    )
