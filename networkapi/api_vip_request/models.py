# -*- coding:utf-8 -*-
import logging

from _mysql_exceptions import OperationalError
from django.core.exceptions import ObjectDoesNotExist
from django.db import models

from networkapi.ambiente.models import EnvironmentVip
from networkapi.api_vip_request import exceptions
from networkapi.grupo.models import UGrupo
from networkapi.ip.models import Ip
from networkapi.ip.models import Ipv6
from networkapi.models.BaseModel import BaseModel
from networkapi.requisicaovips.models import OptionVip
from networkapi.requisicaovips.models import ServerPool


class VipRequest(BaseModel):
    log = logging.getLogger('VipRequest')

    id = models.AutoField(
        primary_key=True,
    )

    created = models.BooleanField(
        default=False,
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

    @classmethod
    def get_by_pk(cls, id):
        """"Get Vip Request by id.

        @return: Vip Request.

        @raise VipRequestNotFoundError: Vip Request not registered.
        @raise VipRequestError: Failed to search for the Vip Request.
        @raise OperationalError: Lock wait timeout exceeded.
        """
        try:
            return VipRequest.objects.get(id=id)
        except ObjectDoesNotExist, e:
            cls.log.error(u'vip request not found. pk {}'.format(id))
            raise exceptions.VipRequestNotFoundError(id)
        except OperationalError, e:
            cls.log.error(u'Lock wait timeout exceeded.')
            raise OperationalError(
                e, u'Lock wait timeout exceeded; try restarting transaction')
        except Exception, e:
            cls.log.error(u'Failure to search the option vip.')
            raise exceptions.VipRequestError(e, u'Failure to search the vip request.')


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

    @classmethod
    def get_by_pk(cls, id):
        """"Get Vip Request Option Vip by id.

        @return: Vip Request Option Vip.

        @raise VipRequestOptionVipNotFoundError: Vip Request Option Vip not registered.
        @raise VipRequestOptionVipError: Failed to search for the Vip Request Option Vip.
        @raise OperationalError: Lock wait timeout exceeded.
        """
        try:
            return VipRequestOptionVip.objects.get(id=id)
        except ObjectDoesNotExist, e:
            cls.log.error(u'vip request option vip not found. pk {}'.format(id))
            raise exceptions.VipRequestOptionVipNotFoundError(id)
        except OperationalError, e:
            cls.log.error(u'Lock wait timeout exceeded.')
            raise OperationalError(
                e, u'Lock wait timeout exceeded; try restarting transaction')
        except Exception, e:
            cls.log.error(u'Failure to search the option vip.')
            raise exceptions.VipRequestOptionVipError(e, u'Failure to search the vip request option vip.')


class VipRequestPort(BaseModel):

    id = models.AutoField(
        primary_key=True,
        db_column='id'
    )

    vip_request = models.ForeignKey(
        VipRequest,
        db_column='id_vip_request',
    )

    port = models.IntegerField(
        max_length=5,
        db_column='port'
    )

    identifier = models.CharField(
        max_length=255,
        db_column='identifier',
        null=True
    )

    class Meta(BaseModel.Meta):
        db_table = u'vip_request_port'
        managed = True

    @classmethod
    def get_by_pk(cls, id):
        """"Get Vip Request Port by id.

        @return: Vip Request Port.

        @raise VipRequestPortNotFoundError: Vip Request Port not registered.
        @raise VipRequestPortError: Failed to search for the Vip Request Port.
        @raise OperationalError: Lock wait timeout exceeded.
        """
        try:
            return VipRequestPort.objects.get(id=id)
        except ObjectDoesNotExist, e:
            cls.log.error(u'vip request port not found. pk {}'.format(id))
            raise exceptions.VipRequestPortNotFoundError(id)
        except OperationalError, e:
            cls.log.error(u'Lock wait timeout exceeded.')
            raise OperationalError(
                e, u'Lock wait timeout exceeded; try restarting transaction')
        except Exception, e:
            cls.log.error(u'Failure to search the option vip.')
            raise exceptions.VipRequestPortError(e, u'Failure to search the vip request port.')


class VipRequestPortOptionVip(BaseModel):

    id = models.AutoField(
        primary_key=True,
        db_column='id'
    )

    vip_request_port = models.ForeignKey(
        VipRequestPort,
        db_column='id_vip_request_port',
    )

    optionvip = models.ForeignKey(
        OptionVip,
        db_column='id_opcoesvip',
    )

    class Meta(BaseModel.Meta):
        db_table = u'vip_request_port_optionsvip'
        managed = True

    @classmethod
    def get_by_pk(cls, id):
        """"Get Vip Request Port Option Vip by id.

        @return: Vip Request Port Option Vip.

        @raise VipRequestPortOptionVipNotFoundError: Vip Request Port Option Vip not registered.
        @raise VipRequestPortOptionVipError: Failed to search for the Vip Request Port Option Vip.
        @raise OperationalError: Lock wait timeout exceeded.
        """
        try:
            return VipRequestPortOptionVip.objects.get(id=id)
        except ObjectDoesNotExist, e:
            cls.log.error(u'vip request port option vip not found. pk {}'.format(id))
            raise exceptions.VipRequestPortOptionVipNotFoundError(id)
        except OperationalError, e:
            cls.log.error(u'Lock wait timeout exceeded.')
            raise OperationalError(
                e, u'Lock wait timeout exceeded; try restarting transaction')
        except Exception, e:
            cls.log.error(u'Failure to search the option vip.')
            raise exceptions.VipRequestPortOptionVipError(e, u'Failure to search the vip request port option vip.')


class VipRequestPortPool(BaseModel):

    id = models.AutoField(
        primary_key=True,
        db_column='id'
    )

    vip_request_port = models.ForeignKey(
        VipRequestPort,
        db_column='id_vip_request_port',
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
        null=True
    )

    order = models.IntegerField(
        null=True
    )

    class Meta(BaseModel.Meta):
        db_table = u'vip_request_port_pool'
        managed = True

    @classmethod
    def get_by_pk(cls, id):
        """"Get Vip Request Port Pool by id.

        @return: Vip Request Port Pool.

        @raise VipRequestPortPoolNotFoundError: Vip Request Port Pool not registered.
        @raise VipRequestPortPoolError: Failed to search for the Vip Request Port Pool.
        @raise OperationalError: Lock wait timeout exceeded.
        """
        try:
            return VipRequestPortPool.objects.get(id=id)
        except ObjectDoesNotExist, e:
            cls.log.error(u'vip request port pool not found. pk {}'.format(id))
            raise exceptions.VipRequestPortPoolNotFoundError(id)
        except OperationalError, e:
            cls.log.error(u'Lock wait timeout exceeded.')
            raise OperationalError(
                e, u'Lock wait timeout exceeded; try restarting transaction')
        except Exception, e:
            cls.log.error(u'Failure to search the option vip.')
            raise exceptions.VipRequestPortPoolError(e, u'Failure to search the vip request port pool.')


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

    @classmethod
    def get_by_pk(cls, id):
        """"Get Vip Request DSCP by id.

        @return: Vip Request DSCP.

        @raise VipRequestDscpNotFoundError: Vip Request DSCP not registered.
        @raise VipRequestDscpError: Failed to search for the Vip Request DSCP.
        @raise OperationalError: Lock wait timeout exceeded.
        """
        try:
            return VipRequestDSCP.objects.get(id=id)
        except ObjectDoesNotExist, e:
            cls.log.error(u'vip request dscp not found. pk {}'.format(id))
            raise exceptions.VipRequestDSCPNotFoundError(id)
        except OperationalError, e:
            cls.log.error(u'Lock wait timeout exceeded.')
            raise OperationalError(
                e, u'Lock wait timeout exceeded; try restarting transaction')
        except Exception, e:
            cls.log.error(u'Failure to search the option vip.')
            raise exceptions.VipRequestDSCPError(e, u'Failure to search the vip request dscp.')


class VipRequestGroupPermission(BaseModel):
    id = models.AutoField(primary_key=True, db_column='id')
    user_group = models.ForeignKey(UGrupo, db_column='id_user_group')
    vip_request = models.ForeignKey(VipRequest, db_column='id_vip_request')
    read = models.BooleanField()
    write = models.BooleanField()
    change_config = models.BooleanField()
    delete = models.BooleanField()

    class Meta(BaseModel.Meta):
        db_table = u'vip_request_group_permission'
        managed = True
        unique_together = ('user_group', 'vip_request')

    @classmethod
    def get_by_pk(cls, id):
        """"Get Vip Request Group Permission by id.

        @return: Vip Request Group Permission.

        @raise VipRequestGroupPermissionNotFoundError: Vip Request Group Permission not registered.
        @raise VipRequestGroupPermissionError: Failed to search for the Vip Request Group Permission.
        @raise OperationalError: Lock wait timeout exceeded.
        """
        try:
            return VipRequestGroupPermission.objects.get(id=id)
        except ObjectDoesNotExist, e:
            cls.log.error(u'vip request group permission not found. pk {}'.format(id))
            raise exceptions.VipRequestGroupPermissionNotFoundError(id)
        except OperationalError, e:
            cls.log.error(u'Lock wait timeout exceeded.')
            raise OperationalError(
                e, u'Lock wait timeout exceeded; try restarting transaction')
        except Exception, e:
            cls.log.error(u'Failure to search the option vip.')
            raise exceptions.VipRequestGroupPermissionError(e, u'Failure to search the vip request group permission.')
