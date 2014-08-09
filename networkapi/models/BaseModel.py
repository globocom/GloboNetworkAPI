# -*- coding:utf-8 -*-
'''
Title: Infrastructure NetworkAPI
Author: globo.com / TQI
Copyright: ( c )  2009 globo.com todos os direitos reservados.
'''

from django.db import models, transaction, router
from networkapi.models.BaseManager import BaseManager
from django.db.models.deletion import Collector


class BaseModel(models.Model):

    '''
    Classe básica para as classes que herdam de "django.db.models.Model".

    Deverão herdar desta classe as classes "Model" que necessitam gerar log das 
    suas operações de escrita e exclusão de dados no banco de dados.
    '''

    objects = BaseManager()

    class Meta:
        abstract = True

    def set_authenticated_user(self, user):
        self.authenticated_user = user

    def save(self, user, force_insert=False, force_update=False, commit=False):
        self.set_authenticated_user(user)
        super(BaseModel, self).save(force_insert, force_update)
        if commit == True:
            transaction.commit()

    def delete(self, user):
        '''
        Replace  super(BaseModel, self).delete()
        Cause: When delete relationship in cascade  default no have attribute User to Log.
        '''
        using = router.db_for_write(self.__class__, instance=self)
        assert self._get_pk_val() is not None, "%s object can't be deleted because its %s attribute is set to None." % (
            self._meta.object_name, self._meta.pk.attname)

        collector = Collector(using=using)
        collector.collect([self])

        for key in collector.data.keys():
            key.authenticated_user = user

        collector.delete()
