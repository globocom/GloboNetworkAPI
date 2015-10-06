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


from django.db import models

from networkapi.ambiente.models import Ambiente

from django.core.exceptions import ObjectDoesNotExist

import logging

from networkapi.models.BaseModel import BaseModel


class HealthcheckExpectError(Exception):

    """Representa um erro ocorrido durante acesso à tabelas relacionadas com HealthcheckExpect."""

    def __init__(self, cause, message=None):
        self.cause = cause
        self.message = message

    def __str__(self):
        msg = u'Causa: %s, Mensagem: %s' % (self.cause, self.message)
        return msg.encode('utf-8', 'replace')


class HealthcheckExpectNotFoundError(HealthcheckExpectError):

    """Retorna exceção para pesquisa de HealthcheckExpect por chave primária."""

    def __init__(self, cause, message=None):
        HealthcheckExpectError.__init__(self, cause, message)


class HealthcheckEqualError(HealthcheckExpectError):

    """Retorna exceção quando já existe um registro identico ao que será inserido no banco"""

    def __init__(self, cause, message=None):
        HealthcheckExpectError.__init__(self, cause, message)


class HealthcheckExpect(BaseModel):
    id = models.AutoField(primary_key=True, db_column='id_healthcheck_expect')
    expect_string = models.CharField(max_length=50)
    match_list = models.CharField(max_length=50)
    ambiente = models.ForeignKey(Ambiente, db_column='id_ambiente', null=True)

    log = logging.getLogger('HealthcheckExpect')

    class Meta(BaseModel.Meta):
        db_table = u'healthcheck_expect'
        managed = True

    def search(self, environment_id=None):
        try:
            healthcheckexpects = HealthcheckExpect.objects.all()

            if (environment_id is not None):
                healthcheckexpects = healthcheckexpects.filter(
                    ambiente__id=environment_id)

            return healthcheckexpects
        except Exception, e:
            self.log.error(u'Falha ao pesquisar os healthcheck_expects.')
            raise HealthcheckExpectError(
                e, u'Falha ao pesquisar os healthcheck_expects.')

    @classmethod
    def dissociate_environment_and_delete(self, authenticated_user, environment_id=None):
        from networkapi.requisicaovips.models import RequisicaoVips
        try:
            healthcheckexpects = HealthcheckExpect.objects.all()
            if (environment_id is not None):
                hces = healthcheckexpects.filter(ambiente__id=environment_id)
                for hce in hces:
                    vip_criado = False
                    for req_vip in RequisicaoVips.get_by_healthcheck_expect(hce.id):
                        if req_vip.vip_criado:
                            vip_criado = True

                    # If any RequsicaoVips associated, dissociate healthcheck
                    # expect from Ambiente
                    if vip_criado:
                        hce.ambiente = None
                        hce.save(authenticated_user)
                    # Else, delete HealthcheckExpect object
                    else:
                        hce.delete(authenticated_user)

        except Exception, e:
            self.log.error(u'Falha ao desassociar os healthcheck_expects.')
            raise HealthcheckExpectError(
                e, u'Falha ao desassociar os healthcheck_expects.')

    @classmethod
    def get_by_pk(self, id):
        try:
            return HealthcheckExpect.objects.get(pk=id)
        except ObjectDoesNotExist, e:
            raise HealthcheckExpectNotFoundError(
                e, u'Não existe um HealthcheckExpect com a pk = %s.' % id)
        except Exception, e:
            self.log.error(u'Falha ao pesquisar o healthcheck_expect.')
            raise HealthcheckExpectError(
                e, u'Falha ao pesquisar o healthcheck_expect.')

    def insert(self, authenticated_user, match_list, expect_string, environment):
        try:

            try:
                HealthcheckExpect.objects.get(
                    ambiente=environment, match_list=match_list, expect_string=expect_string)
                raise HealthcheckEqualError(None, 'healthcheckexpect com os dados : match_list : %s, expect_string: %s, ambiente_id: % s, já cadastrado' % (
                    match_list, expect_string, str(environment.id)))
            except ObjectDoesNotExist, e:
                pass

            self.ambiente = environment
            self.match_list = match_list
            self.expect_string = expect_string

            self.save()

            return self.id

        except HealthcheckEqualError, e:
            self.log.error(e.message)
            raise HealthcheckEqualError(None, e.message)
        except Exception, e:
            self.log.error(u'Falha ao inserir healthcheck_expect.')
            raise HealthcheckExpectError(
                e, u'Falha ao inserir healthcheck_expect.')

    @classmethod
    def get_expect_strings(self):
        try:
            query = (HealthcheckExpect.objects.values('expect_string')
                     .annotate(id=models.Min('id')))

            return list(query)

        except ObjectDoesNotExist, e:
            self.log.error(u'Healthchecks Does Not Exists.')
            raise HealthcheckExpectNotFoundError(
                e, u'Erro ao pequisar Healthcheks_expects'
            )

        except Exception, e:
            self.log.error(u'Falha ao pesquisar o healthcheck_expect.')
            raise HealthcheckExpectError(
                e, u'Falha ao pesquisar o healthcheck_expect.'
            )

    def insert_expect_string(self, authenticated_user, expect_string, ambiente=None):
        try:

            self.expect_string = expect_string
            self.ambiente = ambiente

            self.save()

            return self.id

        except HealthcheckEqualError, e:
            self.log.error(e.message)
            raise HealthcheckEqualError(None, e.message)
        except Exception, e:
            self.log.error(u'Falha ao inserir healthcheck_expect.')
            raise HealthcheckExpectError(
                e, u'Falha ao inserir healthcheck_expect.')


class Healthcheck(BaseModel):
    id = models.AutoField(primary_key=True, db_column='id_healthcheck')
    identifier = models.CharField(max_length=200)
    healthcheck_type = models.CharField(max_length=45)
    healthcheck_request = models.CharField(max_length=500)
    healthcheck_expect = models.CharField(max_length=200)
    destination = models.CharField(max_length=45, default='*:*')


    log = logging.getLogger('Healthcheck')

    class Meta(BaseModel.Meta):
        db_table = u'healthcheck'
        managed = True