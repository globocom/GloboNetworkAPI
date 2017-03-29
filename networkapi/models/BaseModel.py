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
from django.db import models
from django.db import router
from django.db import transaction
from django.db.models.deletion import Collector

from networkapi.models.BaseManager import BaseManager


class BaseModel(models.Model):

    """
    Classe básica para as classes que herdam de "django.db.models.Model".

    Deverão herdar desta classe as classes "Model" que necessitam gerar log das
    suas operações de escrita e exclusão de dados no banco de dados.
    """

    objects = BaseManager()

    class Meta:
        abstract = True

    def __unicode__(self):
        if hasattr(self, 'nome'):
            return u'{0}'.format(self.nome)
        elif hasattr(self, 'id'):
            return u'{0}'.format(self.id)
        else:
            return u'{0}'.format(self.__str__())

    def set_authenticated_user(self, user):
        self.authenticated_user = user

    def save(self, user=None, force_insert=False, force_update=False, commit=False, **kwargs):
        if user:
            self.set_authenticated_user(user)
        super(BaseModel, self).save(force_insert, force_update, **kwargs)
        if commit is True:
            transaction.commit()

    def delete(self, *args, **kwargs):
        """
        Replace  super(BaseModel, self).delete()
        Cause: When delete relationship in cascade  default no have attribute User to Log.
        """

        using = router.db_for_write(self.__class__, instance=self)
        assert self._get_pk_val() is not None, "%s object can't be deleted because its %s attribute is set to None." % (
            self._meta.object_name, self._meta.pk.attname)

        collector = Collector(using=using)
        collector.collect([self])

        collector.delete()
