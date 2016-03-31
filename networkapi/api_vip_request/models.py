# -*- coding:utf-8 -*-
from django.db import models

from networkapi.ambiente.models import EnvironmentVip
from networkapi.ip.models import Ip, Ipv6
from networkapi.models.BaseModel import BaseModel
from networkapi.requisicaovips.models import OptionVip, ServerPool


class VipRequest(BaseModel):
    id = models.AutoField(
        primary_key=True,
    )

    created = models.BooleanField(
        db_column='created')

    ipv4 = models.ForeignKey(
        Ip,
        db_column='id_ipv4',
        blank=True,
        null=True
    )

    ipv6 = models.ForeignKey(
        Ipv6,
        db_column='id_ipv6',
        blank=True,
        null=True
    )

    environmentvip = models.ForeignKey(
        EnvironmentVip,
        db_column='id_environmentvip',
        blank=True,
        null=True
    )

    business = models.CharField(
        max_length=255,
        db_column='business',
        null=True)

    service = models.CharField(
        max_length=255,
        db_column='service',
        null=True)

    name = models.CharField(
        max_length=255,
        db_column='name',
        null=True)

    class Meta(BaseModel.Meta):
        db_table = u'vip_request'
        managed = True


class VipRequestOptionVip(BaseModel):

    id = models.AutoField(
        primary_key=True,
        db_column='id'
    )

    vip_request = models.ForeignKey(
        VipRequest,
        db_column='id_vip_request',
    )

    optionvip = models.ForeignKey(
        OptionVip,
        db_column='id_opcoesvip',
    )

    class Meta(BaseModel.Meta):
        db_table = u'vip_request_optionsvip'
        managed = True


class VipRequestPool(BaseModel):

    id = models.AutoField(
        primary_key=True,
        db_column='id'
    )

    vip_request = models.ForeignKey(
        VipRequest,
        db_column='id_vip_request',
    )

    optionvip = models.ForeignKey(
        OptionVip,
        db_column='id_opcoesvip',
    )

    server_pool = models.ForeignKey(
        ServerPool,
        db_column='id_server_pool',
    )

    val_optionvip = models.CharField(
        max_length=255,
        db_column='val_optionvip',
        blank=True,
        null=True)

    port = models.IntegerField(
        max_length=5,
        db_column='port')

    class Meta(BaseModel.Meta):
        db_table = u'vip_request_pool'
        managed = True


class VipRequestDSCP(BaseModel):

    id = models.AutoField(
        primary_key=True,
        db_column='id'
    )

    vip_request = models.ForeignKey(
        VipRequest,
        db_column='id_vip_request',
    )

    dscp = models.IntegerField(
        max_length=2,
        db_column='dscp')

    class Meta(BaseModel.Meta):

        db_table = u'vip_request_dscp'
        managed = True
