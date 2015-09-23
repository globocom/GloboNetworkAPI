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


from django.db.models.signals import post_save, post_delete
from networkapi.eventlog.models import EventLog
from networkapi.models.BaseModel import BaseModel

import collections

from functools import wraps

def disable_for_loaddata(signal_handler):
    """
    Decorator that turns off signal handlers when loading fixture data.
    """

    @wraps(signal_handler)
    def wrapper(*args, **kwargs):
        if kwargs['raw']:
            return
        signal_handler(*args, **kwargs)
    return wrapper

class MissingUserError(Exception):

    """Representa um erro ocorrido quando a instância salva ou excluída não possuir a informação 'authenticated_user'."""

    def __init__(self, cause=None):
        self.cause = cause

    def __str__(self):
        msg = u'Causa: %s, Mensagem: A instância não possui o atributo "authenticated_user" ou o valor do mesmo está vazio.' % self.cause
        return msg.encode('utf-8', 'replace')

# Método que processará o signal enviado após a invocação do método save
# dos models


def networkapi_post_save(sender, instance, created, **kwargs):

    # Não podemos logar o save da classe EventLog já que isso invocaria um
    # novo signal gerando um loop infinito
    if (not issubclass(instance.__class__, BaseModel)) or (instance.__class__ is EventLog):
        return

    # Define dados do log

    event = dict()
    tipo = ''

    try:
        user = instance.authenticated_user
    except Exception, e:
        raise MissingUserError(e)

    if user is None:
        raise MissingUserError()

    values_map = dict(instance.__dict__)
    del values_map['authenticated_user']

    if (values_map['id']):
        id_objeto = values_map['id']
    else:
        id_objeto = 0

    parametro_atual = ''
    parametro_anterior = ''

    for val in values_map:
        if not (str(val) == '_state'):
            if not str(val)[0] == '_':
                if str(val) == 'pwd' or str(val) == 'password' or str(val) == 'enable_pass':
                    parametro_atual += str(val) + ' = ******** / '
                else:
                    parametro_atual += str(val) + \
                        ' = ' + str(values_map[val]) + ' / '

    if created:

        event['acao'] = 'Cadastrar'
        event['funcionalidade'] = instance.__class__.__name__
        event['parametro_anterior'] = '-'
        event['parametro_atual'] = parametro_atual
        event['id_objeto'] = id_objeto

        #event = 'Inserir na tabela ' + instance._meta.db_table + ' o registro ' + values_map.__repr__() + '.'

    else:

        classe = instance.__class__

        if (values_map['id']):
            id_objeto = values_map['id']
            try:
                parametro_anterior = EventLog.objects.values_list('parametro_atual', flat=True).filter(
                    id_objeto=id_objeto, funcionalidade=classe.__name__).order_by("-id")[0]
            except:
                parametro_anterior = ''

        else:
            parametro_anterior = "parametro anterior"

        event['acao'] = 'Alterar'
        event['funcionalidade'] = classe.__name__
        event['parametro_anterior'] = parametro_anterior
        event['parametro_atual'] = parametro_atual
        event['id_objeto'] = id_objeto

        #event = 'Alterar a tabela ' + instance._meta.db_table + '. Registro alterado: ' + values_map.__repr__() + '.'

    EventLog.log(user, event)

# Método que processará o signal enviado após a invocação do método delete
# dos models


def networkapi_post_delete(sender, instance, **kwargs):
    # Define dados do log

    event = dict()

    try:
        user = instance.authenticated_user
    except Exception, e:
        raise MissingUserError(e)

    if user is None:
        raise MissingUserError()

    values_map = dict(instance.__dict__)

    if (values_map['id']):
        id_objeto = values_map['id']
    else:
        id_objeto = 0

    parametro_anterior = ''

    for val in values_map:
        if not (str(val) == '_state'):
            if not str(val)[0] == '_':
                if str(val) == 'pwd' or str(val) == 'password' or str(val) == 'enable_pass':
                    parametro_anterior += str(val) + ' = ******** / '
                else:
                    parametro_anterior += str(val) + \
                        ' = ' + str(values_map[val]) + ' / '

    event['acao'] = 'Remover'
    event['funcionalidade'] = instance.__class__.__name__
    event['parametro_anterior'] = parametro_anterior
    event['parametro_atual'] = '-'
    event['id_objeto'] = id_objeto

    #event = 'Excluir da tabela ' + instance._meta.db_table + ' o registro ' + values_map.__repr__() + '.'

    # Salva o log
    EventLog.log(user, event)


# Registra os processadores de signals post_save e post_delete
post_save.connect(networkapi_post_save)
post_delete.connect(networkapi_post_delete)
