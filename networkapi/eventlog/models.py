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
import threading
from datetime import datetime
from time import time

from django.db import models
from django.utils.translation import ugettext_lazy as _

from networkapi.queue_tools.rabbitmq import QueueManager

LOG = logging.getLogger(__name__)


class EventLogError(Exception):

    """Representa um erro ocorrido durante acesso à tabela event_log."""

    def __init__(self, cause, message=None):
        self.cause = cause
        self.message = message

    def __str__(self):
        msg = u'Causa: %s, Mensagem: %s' % (self.cause, self.message)
        return msg.encode('utf-8', 'replace')


class EventLog(models.Model):

    ADD = 0
    CHANGE = 1
    DELETE = 2

    id = models.AutoField(primary_key=True, db_column='id_evento')
    usuario = models.ForeignKey(
        'usuario.Usuario',
        db_column='id_user',
        blank=True,
        null=True
    )
    hora_evento = models.DateTimeField()
    acao = models.TextField()
    funcionalidade = models.TextField()
    parametro_anterior = models.TextField()
    parametro_atual = models.TextField()
    evento = models.TextField()
    resultado = models.IntegerField()
    id_objeto = models.IntegerField()
    audit_request = models.ForeignKey(
        'eventlog.AuditRequest',
        db_column='id_audit_request',
        blank=True,
        null=True
    )

    logger = logging.getLogger('EventLog')

    class Meta:
        db_table = u'event_log'
        managed = True

    @classmethod
    def log(cls, usuario, evento):
        """
        saves the eventlog in the database
        @params
        usuario: Usuario object
        evento: dict in the form
        {
            "acao": value,
            "funcionalidade": value,
            "parametro_anterior": value,
            "parametro_atual": value,
            "id_objeto": value,
            "audit_request": value
        }
        """

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
            event_log.audit_request = evento['audit_request']
            event_log.evento = ''
            event_log.resultado = 0
            event_log.save()
        except Exception, e:
            cls.logger.error(
                u'Falha ao salvar o log: evento = %s, id do usuario = %s.' % (evento, usuario))
            raise EventLogError(
                e, u'Falha ao salvar o log: evento = %s, id do usuario = %s.' % (evento, usuario))


class EventLogQueue(object):

    @classmethod
    def log(cls, usuario, evento):
        """Send the eventlog to queues"""

        usuario_id = 'NoUser'
        if usuario:
            usuario_id = usuario.id

        # Send to Queue
        queue_manager = QueueManager(
            broker_vhost='tasks',
            queue_name='tasks.eventlog',
            exchange_name='tasks.eventlog',
            routing_key='tasks.eventlog')

        queue_manager.append({
            'action': evento['acao'],
            'kind': evento['funcionalidade'],
            'timestamp': int(time()),
            'data': {
                'id_object': evento['id_objeto'],
                'user': usuario_id,
                'old_value': evento['parametro_anterior'],
                'new_value': evento['parametro_atual']
            }
        })
        queue_manager.send()


class AuditRequest(models.Model):

    """
    copied from https://github.com/leandrosouza/django-simple-audit
    """

    THREAD_LOCAL = threading.local()

    request_id = models.CharField(max_length=255)
    request_context = models.CharField(max_length=255)
    ip = models.IPAddressField()
    path = models.CharField(max_length=1024)
    date = models.DateTimeField(auto_now_add=True, verbose_name=_('Date'))
    user = models.ForeignKey('usuario.Usuario')

    class Meta:
        db_table = u'audit_request'

    @staticmethod
    def new_request(path, user, ip, identity, context):
        """
        Create a new request from a path, user and ip and put it on thread context.
        The new request should not be saved until first use or calling method current_request(True)
        """
        from networkapi.usuario.models import Usuario

        if not isinstance(user, Usuario):

            # try to find a Usuario with the same email
            # Need to do this because we are using django 1.4 and we cannot
            # change the user model
            usuario, created = Usuario.objects.get_or_create(
                user=user.username,
                defaults={'ativo': user.is_active,
                          'nome': user.get_full_name(),
                          'email': user.email,
                          'user': user.username})

        else:
            usuario = user

        audit_request = AuditRequest()
        audit_request.ip = ip
        audit_request.user = usuario
        audit_request.path = path
        audit_request.request_id = identity
        audit_request.request_context = context

        AuditRequest.THREAD_LOCAL.current = audit_request
        return audit_request

    @staticmethod
    def set_request_from_id(request_id):
        """
        Load an old request from database and put it again in thread context.
        If request_id doesn'texist, thread context will be cleared
        """

        audit_request = None
        if request_id is not None:
            try:
                audit_request = AuditRequest.objects.get(request_id=request_id)
            except AuditRequest.DoesNotExist:
                pass

        AuditRequest.THREAD_LOCAL.current = audit_request

    @staticmethod
    def current_request(force_save=False):
        """
        Get current request from thread context (or None doesn't exist).

        If you specify force_save,current request will be saved on database first.
        """

        audit_request = getattr(AuditRequest.THREAD_LOCAL, 'current', None)
        if force_save and audit_request is not None and audit_request.pk is None:
            audit_request.save()
        return audit_request

    @staticmethod
    def cleanup_request():
        """
        Remove audit request from thread context
        """
        AuditRequest.THREAD_LOCAL.current = None


class Functionality(models.Model):
    nome = models.CharField(
        max_length=50, primary_key=True, db_column='functionality')

    logger = logging.getLogger('Funcionality')

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
