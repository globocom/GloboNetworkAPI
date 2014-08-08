# -*- coding:utf-8 -*-
'''
Title: Infrastructure NetworkAPI
Author: globo.com / TQI
Copyright: ( c )  2009 globo.com todos os direitos reservados.
'''
from __future__ import with_statement
from django.db import models
from networkapi.log import Log
from networkapi.models.BaseModel import BaseModel
from django.core.exceptions import ObjectDoesNotExist
from networkapi.distributedlock import distributedlock, LOCK_TYPE_ACCESS

class TipoAcessoError(Exception):
    """Representa um erro ocorrido durante acesso à tabelas relacionadas com Tipo de Acesso."""
    def __init__(self, cause, message=None):
        self.cause = cause
        self.message = message
        
    def __str__(self):
        msg = u'Causa: %s, Mensagem: %s' % (self.cause, self.message) 
        return msg.encode('utf-8', 'replace')

class DuplicateProtocolError(TipoAcessoError):
    """Retorna exceção se houver tentativa de gravação de tipo de acesso com protocolo duplicado."""
    def __init__(self, cause, message=None):
        TipoAcessoError.__init__(self, cause, message)


class AccessTypeUsedByEquipmentError(TipoAcessoError):
    """Retorna exceção se houver tentativa de exclusão de tipo de acesso utilizado por algum equipamento."""
    def __init__(self, cause, message=None):
        TipoAcessoError.__init__(self, cause, message)
        
class AccessTypeNotFoundError(TipoAcessoError):
    """Retorna exceção para pesquisa de tipo de acesso por chave primária."""
    def __init__(self,cause,message=None):
        TipoAcessoError.__init__(self, cause, message)  

class TipoAcesso(BaseModel):
    """Classe que representa a entidade Tipo de Acesso (tabela tipo_acesso)"""
    
    id = models.AutoField(primary_key=True, db_column='id_tipo_acesso')
    protocolo = models.CharField(unique=True, max_length=45)

    log = Log('TipoAcesso')
    
    class Meta(BaseModel.Meta):
        db_table = u'tipo_acesso'
        managed = True
    
    @classmethod
    def get_by_pk(cls, pk):
        try:
            return TipoAcesso.objects.get(pk=pk)
        except ObjectDoesNotExist, e:
            raise AccessTypeNotFoundError(e, u'Não existe um tipo de acesso com a pk = %s.' % pk)        
        except Exception, e:
            cls.log.error(u'Falha ao pesquisar o tipo de acesso.')
            raise TipoAcessoError(e, u'Falha ao pesquisar o tipo de acesso.')
    