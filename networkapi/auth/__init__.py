# -*- coding:utf-8 -*-

'''
Title: Infrastructure NetworkAPI
Author: globo.com / TQI
Copyright: ( c )  2009 globo.com todos os direitos reservados.
'''

from networkapi.usuario.models import Usuario

from networkapi.grupo.models import PermissaoAdministrativa, UGrupo, DireitosGrupoEquipamento, EGrupo, EGrupoNotFoundError, PermissaoAdministrativaNotFoundError, GrupoError

from networkapi.equipamento.models import Equipamento, EquipamentoNotFoundError

from networkapi.admin_permission import AdminPermission


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


def has_perm(
        user,
        perm_function,
        perm_oper,
        egroup_id=None,
        equip_id=None,
        equip_oper=None):
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
        equip = Equipamento().get_by_pk(equip_id)
        egroups = equip.grupos.all()
        if len(egroups) == 0:
            return False

    ugroups = user.grupos.all()
    for ugroup in ugroups:
        try:
            perm = PermissaoAdministrativa().get_permission(
                perm_function,
                ugroup,
                perm_oper)
            if (egroups is None) or (
                    _has_equip_perm(ugroup, egroups, equip_oper)):
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
