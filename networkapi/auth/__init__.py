# -*- coding:utf-8 -*-
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
from networkapi.api_vip_request.models import VipRequest
from networkapi.equipamento.models import Equipamento
from networkapi.equipamento.models import EquipamentoNotFoundError
from networkapi.grupo.models import DireitosGrupoEquipamento
from networkapi.grupo.models import EGrupo
from networkapi.grupo.models import EGrupoNotFoundError
from networkapi.grupo.models import GrupoError
from networkapi.grupo.models import PermissaoAdministrativa
from networkapi.grupo.models import PermissaoAdministrativaNotFoundError
from networkapi.grupo.models import UGrupo
from networkapi.requisicaovips.models import ServerPool
from networkapi.usuario.models import Usuario

log = logging.getLogger(__name__)


def authenticate(username, password, user_ldap=None):
    '''Busca o usuário com ativo com o login e senha informados.

    @raise UsuarioError: Falha ao pesquisar o usuário.
    '''
    if username is None or password is None:
        return None

    if user_ldap is None:
        return Usuario().get_enabled_user(username, password)
    else:
        return Usuario().get_by_ldap_user(user_ldap, True)


def has_perm(user, perm_function, perm_oper, egroup_id=None, equip_id=None, equip_oper=None):
    '''
    @raise EGrupoNotFoundError: Grupo do equipamento nao cadastrado.

    @raise EquipamentoNotFoundError: Equipamento nao cadastrado.

    @raise GrupoError: Falha ao pesquisar os direitos do grupo-equipamento, ou as permissões administrativas, ou o grupo do equipamento.

    @raise EquipamentoError: Falha ao pesquisar o equipamento.
    '''
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


def validate_pool_perm(pools, user, pool_operation):

    if len(pools) == 0:
        return False

    server_pools = ServerPool.objects.filter(id__in=pools)
    for pool in server_pools:

        perms = pool.serverpoolgrouppermission_set.all()

        if not perms:
            return True

        ugroups = user.grupos.all()

        if perms:

            pool_perm = _validate_obj(perms, ugroups, pool_operation)
            if not pool_perm:
                log.warning('User{} does not have permission {} to Pool {}'.format(
                    user, pool_operation, pool.id
                ))
                return False

    return True


def validate_vip_perm(vips, user, vip_operation):

    if len(vips) == 0:
        return False

    vips_request = VipRequest.objects.filter(id__in=vips)
    for vip in vips_request:

        perms = vip.viprequestgrouppermission_set.all()

        if not perms:
            return True

        ugroups = user.grupos.all()

        if perms:

            vip_perm = _validate_obj(perms, ugroups, vip_operation)
            if not vip_perm:
                log.warning('User{} does not have permission {} to Vip {}'.format(
                    user, vip_operation, vip.id
                ))
                return False

    return True


def _validate_obj(perms, ugroups, pool_operation):
    obj_perm = False

    perms = perms.filter(user_group__in=ugroups)

    if pool_operation == AdminPermission.POOL_READ_OPERATION:
        perms = perms.filter(read=True)
    elif pool_operation == AdminPermission.POOL_WRITE_OPERATION:
        perms = perms.filter(write=True)
    elif pool_operation == AdminPermission.POOL_DELETE_OPERATION:
        perms = perms.filter(delete=True)
    elif pool_operation == AdminPermission.POOL_UPDATE_CONFIG_OPERATION:
        perms = perms.filter(change_config=True)

    if perms:
        obj_perm = True

    return obj_perm


def perm_pool(request, operation, *args, **kwargs):
    pools = kwargs.get('pool_ids').split(';')
    return validate_pool_perm(
        pools,
        request.user,
        operation
    )


def perm_vip(request, operation, *args, **kwargs):

    vips = kwargs.get('vip_request_ids').split(';')
    return validate_vip_perm(
        vips,
        request.user,
        operation
    )
