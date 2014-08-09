# -*- coding:utf-8 -*-
'''
Title: Infrastructure NetworkAPI
Author: globo.com / TQI
Copyright: ( c )  2009 globo.com todos os direitos reservados.
'''

from django.db import models

from django.core.exceptions import ObjectDoesNotExist

from networkapi.admin_permission import AdminPermission

from networkapi.log import Log

from networkapi.models.BaseModel import BaseModel


class GrupoError(Exception):

    """Representa um erro ocorrido durante acesso à tabelas relacionadas com Grupos."""

    def __init__(self, cause, message=None):
        self.cause = cause
        self.message = message

    def __str__(self):
        msg = u'Causa: %s, Mensagem: %s' % (self.cause, self.message)
        return msg.encode('utf-8', 'replace')


class UGrupoNotFoundError(GrupoError):

    """Retorna exceção para pesquisa de UGrupo por chave primária."""

    def __init__(self, cause, message=None):
        GrupoError.__init__(self, cause, message)


class EGrupoNotFoundError(GrupoError):

    """Retorna exceção para pesquisa de EGrupo por chave primária."""

    def __init__(self, cause, message=None):
        GrupoError.__init__(self, cause, message)


class PermissaoAdministrativaNotFoundError(GrupoError):

    """Retorna exceção para pesquisa de PermissaoAdministrativa por chave primária."""

    def __init__(self, cause, message=None):
        GrupoError.__init__(self, cause, message)


class PermissaoAdministrativaDuplicatedError(GrupoError):

    """Retorna exceção ao tentar inserir uma permissão administrativa com uma funcao e grupo de usuário já cadastrada."""

    def __init__(self, cause, message=None):
        GrupoError.__init__(self, cause, message)


class PermissionError(Exception):

    def __init__(self, cause, message=None):
        self.cause = cause
        self.message = message

    def __str__(self):
        msg = u'Causa: %s, Mensagem: %s' % (self.cause, self.message)
        return msg.encode('utf-8', 'replace')


class PermissionNotFoundError(PermissionError):

    def __init__(self, cause, message=None):
        PermissionError.__init__(self, cause, message)


class UGrupoNameDuplicatedError(GrupoError):

    """Retorna exceção ao tentar inserir um ugrupo com nome já existente."""

    def __init__(self, cause, message=None):
        GrupoError.__init__(self, cause, message)


class EGrupoNameDuplicatedError(GrupoError):

    """Retorna exceção ao tentar inserir um egrupo com nome já existente."""

    def __init__(self, cause, message=None):
        GrupoError.__init__(self, cause, message)


class GroupDontRemoveError(GrupoError):

    def __init__(self, cause, message=None):
        GrupoError.__init__(self, cause, message)


class DireitoGrupoEquipamentoDuplicatedError(GrupoError):

    """Retorna exceção ao tentar inserir um direito grupo equipamento com um grupo de usuário e de equipamento já cadastrado."""

    def __init__(self, cause, message=None):
        GrupoError.__init__(self, cause, message)


class UGrupo(BaseModel):

    id = models.AutoField(primary_key=True)
    nome = models.CharField(unique=True, max_length=100)
    leitura = models.CharField(max_length=1)
    escrita = models.CharField(max_length=1)
    edicao = models.CharField(max_length=1)
    exclusao = models.CharField(max_length=1)

    log = Log('UGrupo')

    class Meta(BaseModel.Meta):
        db_table = u'grupos'
        managed = True

    def delete(self, authenticated_user):
        '''Sobrescreve o método do Django para remover o grupo de usuário.

        Além de remover o grupo também remove as permissões administrativas do grupo,
        os relacionamentos do grupo com usuários e os relacionamentos do grupo com
        grupos de equipamento.
        '''
        for p in self.permissaoadministrativa_set.all():
            p.delete(authenticated_user)
        for ug in self.usuariogrupo_set.all():
            ug.delete(authenticated_user)
        for d in self.direitosgrupoequipamento_set.all():
            d.delete(authenticated_user)

        super(UGrupo, self).delete(authenticated_user)

    @classmethod
    def get_by_pk(cls, id):
        """Get Group User by id.

            @return: Group User.

            @raise UGrupoNotFoundError: Group User is not registered.
            @raise GrupoError: Failed to search for the Group User.
        """
        try:
            return UGrupo.objects.filter(id=id).uniqueResult()
        except ObjectDoesNotExist, e:
            raise UGrupoNotFoundError(
                e, u'Dont there is a Group Use by pk = %s.' % id)
        except Exception, e:
            cls.log.error(u'Failure to search the Group User.')
            raise GrupoError(e, u'Failure to search the Group User.')


class Permission(BaseModel):
    id = models.AutoField(primary_key=True, db_column='id_permission')
    function = models.CharField(max_length=100, unique=True)

    log = Log('Permission')

    class Meta(BaseModel.Meta):
        db_table = u'permissions'
        managed = True

    @classmethod
    def get_by_pk(cls, pk):
        """"Get  Permission by id.

        @return: Permission.

        @raise PermissionNotFoundError: Permission is not registered.
        @raise PermissionError: Failed to search for the Permission.
        """
        try:
            return Permission.objects.get(pk=pk)
        except ObjectDoesNotExist, e:
            raise PermissionNotFoundError(
                e, u'There is Permission with pk = %s.' % pk)
        except Exception, e:
            cls.log.error(u'Failed to search for a Permission.')
            raise PermissionError(e, u'Failed to search for a Permission.')


class PermissaoAdministrativa(BaseModel):
    id = models.AutoField(
        primary_key=True, db_column='id_permissoes_administrativas')
    permission = models.ForeignKey(Permission, db_column='permission_id')
    leitura = models.BooleanField()
    escrita = models.BooleanField()
    ugrupo = models.ForeignKey(UGrupo, db_column='grupos_id')

    log = Log('PermissaoAdministrativa')

    class Meta(BaseModel.Meta):
        db_table = u'permissoes_administrativas'
        managed = True

    def create(self, authenticated_user):
        '''Insere uma nova Permissao Administrativa.

        @return: Nothing

        @raise UGrupo.DoesNotExist: Grupo de usuário não cadastrado.

        @raise GrupoError: Falha ao inserir uma Permissao Administrativa.

        @raise PermissaoAdministrativaDuplicatedError: Permissão administrativa com grupo de usuário e função já cadastrada
        '''

        try:
            PermissaoAdministrativa.get_permission_by_function_ugroup(
                self.funcao, self.ugrupo.id)
            raise PermissaoAdministrativaDuplicatedError(
                None, u'Permissão administrativa com grupo de usuário %s e função %s já cadastrada' % (self.ugrupo.id, self.funcao))
        except PermissaoAdministrativaNotFoundError:
            pass

        try:
            self.ugrupo = UGrupo.objects.get(id=self.ugrupo.id)
            return self.save(authenticated_user)

        except UGrupo.DoesNotExist, e:
            raise e
        except Exception, e:
            self.log.error(u'Falha ao inserir uma Permissao Administrativa.')
            raise GrupoError(
                e, u'Falha ao inserir uma Permissao Administrativa.')

    # ok
    @classmethod
    def get_by_pk(cls, pk):
        """"Get  Administrative Permission by id.

        @return: Administrative Permission.

        @raise PermissaoAdministrativaNotFoundError: Administrative Permission is not registered.
        @raise GrupoError: Failed to search for the Administrative Permission.
        """
        try:
            return PermissaoAdministrativa.objects.get(pk=pk)
        except ObjectDoesNotExist, e:
            raise PermissaoAdministrativaNotFoundError(
                e, u'Não existe uma Permissao Administrativa com a pk = %s.' % pk)
        except Exception, e:
            cls.log.error(u'Falha ao pesquisar uma Permissao Administrativa.')
            raise GrupoError(
                e, u'Falha ao pesquisar uma Permissao Administrativa.')
    # ok

    @classmethod
    def get_permission_by_function_ugroup(cls, function, ugroup_id):
        try:
            return PermissaoAdministrativa.objects.filter(permission__function=function, ugrupo__id=ugroup_id)[0:1].get()
        except ObjectDoesNotExist, o:
            raise PermissaoAdministrativaNotFoundError(
                o, 'Grupo do Usuário %s não tem permissão na função %s.' % (ugroup_id, function))
        except Exception, e:
            cls.log.error(u'Falha ao pesquisar a permissão administrativa.')
            raise GrupoError(
                e, u'Falha ao pesquisar a permissão administrativa.')

    @classmethod
    def get_permission_by_permission_ugroup(cls, permission_id, ugroup_id):
        """"Get  Administrative Permission by id, .

        @return: Administrative Permission.

        @raise PermissaoAdministrativaNotFoundError: Administrative Permission is not registered.
        @raise GrupoError: Failed to search for the Administrative Permission.
        """
        try:
            return PermissaoAdministrativa.objects.filter(permission__id=permission_id, ugrupo__id=ugroup_id)[0:1].get()
        except ObjectDoesNotExist, o:
            # Arrumar MSG
            raise PermissaoAdministrativaNotFoundError(
                o, 'Grupo do Usuário %s não tem permissão na função %s.' % (ugroup_id, permission_id))
        except Exception, e:
            cls.log.error(u'Falha ao pesquisar a permissão administrativa.')
            raise GrupoError(
                e, u'Falha ao pesquisar a permissão administrativa.')

    # ok
    def get_permission(self, function, ugroup, operation):
        q = PermissaoAdministrativa.objects
        try:
            if operation == AdminPermission.WRITE_OPERATION:
                return q.filter(permission__function=function, escrita=1, ugrupo__id=ugroup.id)[0:1].get()
            else:
                return q.filter(permission__function=function, leitura=1, ugrupo__id=ugroup.id)[0:1].get()
        except ObjectDoesNotExist, o:
            raise PermissaoAdministrativaNotFoundError(
                o, 'Grupo do Usuário %s não tem permissão de %s na função %s.' % (ugroup.nome, operation, function))
        except Exception, e:
            self.log.error(
                u'Falha ao pesquisar as permissões administrativas.')
            raise GrupoError(
                e, u'Falha ao pesquisar as permissões administrativas.')


class EGrupo(BaseModel):
    GRUPO_EQUIPAMENTO_ORQUESTRACAO = 1

    id = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=100)

    log = Log('EGrupo')

    class Meta(BaseModel.Meta):
        db_table = u'grupos_equip'
        managed = True

    @classmethod
    def get_by_pk(cls, pk):
        try:
            return EGrupo.objects.get(pk=pk)
        except ObjectDoesNotExist, e:
            raise EGrupoNotFoundError(
                e, u'Não existe um egrupo com a pk = %s.' % pk)
        except Exception, e:
            cls.log.error(u'Falha ao pesquisar o grupo de equipamento.')
            raise GrupoError(e, u'Falha ao pesquisar o grupo de equipamento.')

    @classmethod
    def search(cls):
        try:
            return EGrupo.objects.all()
        except Exception, e:
            cls.log.error(u'Falha ao pesquisar os grupos de equipamento.')
            raise GrupoError(
                e, u'Falha ao pesquisar os grupos de equipamento.')

    def create(self, authenticated_user):
        '''Insere um novo grupo de equipamento.

        @return: Nothing.

        @raise EGrupoNameDuplicatedError: Grupo de equipamento com o nome já cadastrado
        @raise GrupoError: Falha ao inserir o grupo. 
        '''
        try:
            try:
                EGrupo.objects.get(nome__iexact=self.nome)
                raise EGrupoNameDuplicatedError(
                    None, u'Grupo de equipamento com o nome %s já cadastrado' % self.nome)
            except EGrupo.DoesNotExist:
                pass

            self.save(authenticated_user)
        except EGrupoNameDuplicatedError, e:
            raise e
        except Exception, e:
            self.log.error(u'Falha ao inserir o grupo de equipamento.')
            raise GrupoError(e, u'Falha ao inserir o grupo de equipamento.')

    @classmethod
    def update(cls, authenticated_user, pk, **kwargs):
        '''Atualiza os dados de um grupo de equipamento.

        @return: Nothing.

        @raise GrupoError: Falha ao inserir o grupo.

        @raise EGrupoNotFoundError: Grupo de equipamento não cadastrado.

        @raise EGrupoNameDuplicatedError: Grupo de equipamento com o nome já cadastrado.  
        '''
        egrupo = EGrupo.get_by_pk(pk)

        try:

            try:
                nome = kwargs['nome']
                if (egrupo.nome.lower() != nome.lower()):
                    EGrupo.objects.get(nome__iexact=nome)
                    raise EGrupoNameDuplicatedError(
                        None, u'Grupo de equipamento com o nome %s já cadastrado' % nome)
            except (EGrupo.DoesNotExist, KeyError):
                pass

            egrupo.__dict__.update(kwargs)
            egrupo.save(authenticated_user)
        except EGrupoNameDuplicatedError, e:
            raise e
        except Exception, e:
            cls.log.error(u'Falha ao atualizar o grupo de equipamento.')
            raise GrupoError(e, u'Falha ao atualizar o grupo de equipamento.')

    @classmethod
    def remove(cls, authenticated_user, pk):
        egrupo = EGrupo.get_by_pk(pk)

        list_equip = []
        for equipament in egrupo.equipamento_set.all():

            if len(equipament.equipamentogrupo_set.all()) == 1:
                list_equip.append(equipament.nome)

        if len(list_equip) > 0:
            msg = ""
            for equip in list_equip:
                msg = msg + equip + ", "
            raise GroupDontRemoveError(egrupo.nome, msg)

        try:
            egrupo.delete(authenticated_user)
        except Exception, e:
            cls.log.error(u'Falha ao remover o grupo de equipamento.')
            raise GrupoError(e, u'Falha ao remover o grupo de equipamento.')

    def delete(self, authenticated_user):
        '''Sobrescreve o método do Django para remover o grupo de equipamento.

        Além de remover o grupo também remove os relacionamentos do grupo 
        com equipamentos e os relacionamentos do grupo com grupos de usuário.
        '''
        for eg in self.equipamentogrupo_set.all():
            eg.delete(authenticated_user)

        for d in self.direitosgrupoequipamento_set.all():
            d.delete(authenticated_user)

        super(EGrupo, self).delete(authenticated_user)


class DireitosGrupoEquipamento(BaseModel):
    id = models.AutoField(primary_key=True, db_column='id_direito')
    ugrupo = models.ForeignKey(UGrupo, db_column='id_ugrupo')
    egrupo = models.ForeignKey(EGrupo, db_column='id_egrupo')
    leitura = models.BooleanField()
    escrita = models.BooleanField()
    alterar_config = models.BooleanField()
    exclusao = models.BooleanField()

    log = Log('DireitosGrupoEquipamento')

    class Meta(BaseModel.Meta):
        db_table = u'direitos_grupoequip'
        managed = True
        unique_together = ('ugrupo', 'egrupo')

    @classmethod
    def get_by_pk(cls, pk):
        try:
            return DireitosGrupoEquipamento.objects.get(pk=pk)
        except DireitosGrupoEquipamento.DoesNotExist, e:
            raise e
        except Exception, e:
            cls.log.error(
                u'Falha ao pesquisar os direitos de um grupo de usuário em um grupo de equipamento.')
            raise GrupoError(
                e, u'Falha ao pesquisar os direitos de um grupo de usuário em um grupo de equipamento.')

    def create(self, authenticated_user):
        '''Insere um novo direito de um grupo de usuário em um grupo de equipamento.

        @return: Nothing.

        @raise UGrupo.DoesNotExist: Grupo de usuário não cadastrado.
        @raise EGrupoNotFoundError: Grupo de equipamento não cadastrado.
        @raise DireitoGrupoEquipamentoDuplicatedError: Direito Grupo Equipamento já cadastrado. 
        @raise GrupoError: Falha ao inserir o direito.
        '''
        self.egrupo = EGrupo.get_by_pk(self.egrupo.id)

        try:
            self.ugrupo = UGrupo.objects.get(pk=self.ugrupo.id)

            if DireitosGrupoEquipamento.objects.filter(egrupo__id=self.egrupo.id, ugrupo__id=self.ugrupo.id).count() > 0:
                raise DireitoGrupoEquipamentoDuplicatedError(
                    None, u'Direito Grupo Equipamento para o grupo de usuário %d e grupo de equipamento %s já cadastrado.' % (self.ugrupo_id, self.egrupo_id))

            self.save(authenticated_user)
        except UGrupo.DoesNotExist, e:
            raise e
        except DireitoGrupoEquipamentoDuplicatedError, e:
            raise e
        except Exception, e:
            self.log.error(
                u'Falha ao inserir o direito do grupo de usuário no grupo de equipamento.')
            raise GrupoError(
                e, u'Falha ao inserir o direito do grupo de usuário no grupo de equipamento.')

    @classmethod
    def update(cls, authenticated_user, pk, **kwargs):
        '''Atualiza os direitos de um grupo de usuário em um grupo de equipamento.

        @return: Nothing.

        @raise GrupoError: Falha ao alterar os direitos.

        @raise DireitosGrupoEquipamento.DoesNotExist: DireitoGrupoEquipamento não cadastrado.
        '''
        direito = DireitosGrupoEquipamento.get_by_pk(pk)
        try:
            if 'ugrupo_id' in kwargs:
                del kwargs['ugrupo_id']

            if 'ugrupo' in kwargs:
                del kwargs['ugrupo']

            if 'egrupo_id' in kwargs:
                del kwargs['egrupo_id']

            if 'egrupo' in kwargs:
                del kwargs['egrupo']

            direito.__dict__.update(kwargs)
            direito.save(authenticated_user)
        except Exception, e:
            cls.log.error(
                u'Falha ao atualizar os direitos de um grupo de usuário em um grupo de equipamento.')
            raise GrupoError(
                e, u'Falha ao atualizar os direitos de um grupo de usuário em um grupo de equipamento.')

    @classmethod
    def remove(cls, authenticated_user, pk):
        '''Remove os direitos de um grupo de usuário em um grupo de equipamento.

        @raise GrupoError: Falha ao alterar os direitos.

        @raise DireitosGrupoEquipamento.DoesNotExist: DireitoGrupoEquipamento não cadastrado.
        '''
        direito = DireitosGrupoEquipamento.get_by_pk(pk)
        try:
            direito.delete(authenticated_user)
        except Exception, e:
            cls.log.error(
                u'Falha ao remover os direitos de um grupo de usuário em um grupo de equipamento.')
            raise GrupoError(
                e, u'Falha ao remover os direitos de um grupo de usuário em um grupo de equipamento.')

    @classmethod
    def search(cls, ugroup_id=None, equip_operation=None, egroup_id=None):
        try:
            q = DireitosGrupoEquipamento.objects.all()

            if ugroup_id is not None:
                q = q.filter(ugrupo__id=ugroup_id)

            if egroup_id is not None:
                q = q.filter(egrupo__id=egroup_id)

            if equip_operation is not None:
                if equip_operation == AdminPermission.EQUIP_READ_OPERATION:
                    q = q.filter(leitura=True)
                elif equip_operation == AdminPermission.EQUIP_WRITE_OPERATION:
                    q = q.filter(escrita=True)
                elif equip_operation == AdminPermission.EQUIP_UPDATE_CONFIG_OPERATION:
                    q = q.filter(alterar_config=True)

            return q
        except Exception, e:
            cls.log.error(
                u'Falha ao pesquisar os direitos do grupo-equipamento.')
            raise GrupoError(
                e, u'Falha ao pesquisar os direitos do grupo-equipamento.')
