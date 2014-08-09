# -*- coding:utf-8 -*-
'''
Title: Infrastructure NetworkAPI
Author: globo.com / TQI
Copyright: ( c )  2009 globo.com todos os direitos reservados.
'''

from django.db import models

from networkapi.log import Log

class SemaforoError(Exception):
    """Representa um erro ocorrido durante acesso à tabelas relacionadas com semaforo."""
    def __init__(self, cause, message=None):
        self.cause = cause
        self.message = message
        
    def __str__(self):
        msg = u'Causa: %s, Mensagem: %s' % (self.cause, self.message) 
        return msg.encode('utf-8', 'replace')


class Semaforo(models.Model):
    id = models.AutoField(primary_key=True, db_column='id_semaforo')
    descricao = models.CharField(max_length=50)
    
    log = Log('Semaforo')
    
    CRIAR_IP_ID = 1
    ALOCAR_VLAN_ID = 2
    PROVISIONAR_GRUPO_VIRTUAL_ID = 3    
    
    class Meta:
        db_table = u'semaforo'
        managed = False
    
    @classmethod
    def lock(cls, id):
        try:
            semaforo = Semaforo.objects.get(pk=id)
            semaforo.descricao = semaforo.descricao 
            semaforo.save()
        except Exception, e:
            cls.log.error(u'Falha ao realizar o lock para o identificador %s.' % id)
            raise SemaforoError(e, u'Falha ao realizar o lock para o identificador %s.' % id)