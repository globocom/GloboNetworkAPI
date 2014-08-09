# -*- coding:utf-8 -*-
'''
Title: Configurations NetworkAPI
Author: avanzolin
Copyright: ( c )  2009 globo.com todos os direitos reservados.
'''

from networkapi.models.BaseModel import BaseModel
from networkapi.log import Log
from django.db import models


class Configuration(BaseModel):
    id = models.AutoField(primary_key=True, db_column='id_config')
    IPv4_MIN = models.SmallIntegerField(db_column='ip_v4_min')
    IPv4_MAX = models.SmallIntegerField(db_column='ip_v4_max')
    IPv6_MIN = models.SmallIntegerField(db_column='ip_v6_min')
    IPv6_MAX = models.SmallIntegerField(db_column='ip_v6_max')

    log = Log('Configuration')

    class Meta(BaseModel.Meta):
        db_table = u'config'
        managed = True

    @classmethod
    def get(cls):
        return Configuration.objects.all()[0]
