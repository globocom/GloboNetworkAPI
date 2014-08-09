# -*- coding:utf-8 -*-
'''
Title: Infrastructure NetworkAPI
Author: globo.com / TQI
Copyright: ( c )  2009 globo.com todos os direitos reservados.
'''

from django.db import models
from datetime import datetime
from networkapi.models.BaseModel import BaseModel
from networkapi.usuario.models import Usuario
from networkapi.log import Log


class EventLogError(Exception):

    """Representa um erro ocorrido durante acesso à tabela event_log."""

    def __init__(self, cause, message=None):
        self.cause = cause
        self.message = message

    def __str__(self):
        msg = u'Causa: %s, Mensagem: %s' % (self.cause, self.message)
        return msg.encode('utf-8', 'replace')


class EventLog(BaseModel):
    id = models.AutoField(primary_key=True, db_column='id_evento')
    usuario = models.ForeignKey(Usuario, db_column='id_user')
    hora_evento = models.DateTimeField()
    acao = models.TextField()
    funcionalidade = models.TextField()
    parametro_anterior = models.TextField()
    parametro_atual = models.TextField()
    evento = models.TextField()
    resultado = models.IntegerField()
    id_objeto = models.IntegerField()

    logger = Log('EventLog')

    class Meta(BaseModel.Meta):
        db_table = u'event_log'
        managed = True

    @classmethod
    def log(cls, usuario, evento):
        """ Gera um log da operação realizada pelo usuário """

        try:
            functionality = Functionality()
            event_log = EventLog()
            event_log.usuario = usuario
            event_log.hora_evento = datetime.now()
            event_log.acao = evento['acao']
            event_log.funcionalidade = functionality.exist(
                evento['funcionalidade'])
            event_log.parametro_anterior = evento['parametro_anterior']
            event_log.parametro_atual = evento['parametro_atual']
            event_log.id_objeto = evento['id_objeto']
            event_log.evento = ''
            event_log.resultado = 0
            event_log.save(usuario)
        except Exception as e:
            cls.logger.error(
                u'Falha ao salvar o log: evento = %s, id do usuario = %s.' %
                (evento, usuario.id))
            raise EventLogError(
                e, u'Falha ao salvar o log: evento = %s, id do usuario = %s.' %
                (evento, usuario.id))

    @classmethod
    def uniqueUsers(cls):
        userlist = EventLog.objects.only(
            'usuario').filter().group_by('id_user')
        return userlist


class Functionality(models.Model):
    nome = models.CharField(
        max_length=50,
        primary_key=True,
        db_column='functionality')

    logger = Log('Funcionality')

    class Meta:
        db_table = u'functionality'

    @classmethod
    def exist(cls, event_functionality):
        func = Functionality.objects.filter(nome=event_functionality)
        if func.exists():
            return event_functionality
        else:
            functionality = Functionality()
            functionality.nome = event_functionality
            functionality.save()
            return event_functionality
