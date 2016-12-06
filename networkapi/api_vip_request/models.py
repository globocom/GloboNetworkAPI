# -*- coding: utf-8 -*-
import logging

from _mysql_exceptions import OperationalError
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models import get_model

from networkapi.api_vip_request import exceptions
from networkapi.api_vip_request import syncs
from networkapi.models.BaseModel import BaseModel
from networkapi.util.decorators import cached_property


class VipRequest(BaseModel):

    log = logging.getLogger('VipRequest')

    id = models.AutoField(
        primary_key=True,
    )

    created = models.BooleanField(
        default=False,
        db_column='created')

    ipv4 = models.ForeignKey(
        'ip.Ip',
        db_column='id_ipv4',
        blank=True,
        null=True
    )

    ipv6 = models.ForeignKey(
        'ip.Ipv6',
        db_column='id_ipv6',
        blank=True,
        null=True
    )

    environmentvip = models.ForeignKey(
        'ambiente.EnvironmentVip',
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

    @cached_property
    def dscp(self):
        return self.viprequestdscp_set.get().dscp

    @cached_property
    def equipments(self):
        eqpts = list()
        if self.ipv4:
            eqpts = self.ipv4.ipequipamento_set.all().prefetch_related('equipamento')
        if self.ipv6:
            eqpts |= self.ipv6.ipv6equipament_set.all().prefetch_related('equipamento')
        eqpts = [eqpt.equipamento for eqpt in eqpts]
        return eqpts

    @cached_property
    def default_names(self):
        names = [port.identifier for port in self.viprequestport_set.all()]
        names = list(set(names))
        return names

    @cached_property
    def ports(self):
        ports = self.viprequestport_set.all()
        return ports

    @cached_property
    def options(self):
        options = self.viprequestoptionvip_set.all()
        return options

    @cached_property
    def groups_permissions(self):
        perms = self.viprequestgrouppermission_set.all()
        return perms

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
            raise exceptions.VipRequestError(
                e, u'Failure to search the vip request.')

    def delete_v3(self, bypass_ipv4=False, bypass_ipv6=False, sync=True):
        """
        Delete Vip Request

        @raise VipConstraintCreated: Vip request can not be deleted
                                     because it is created in equipment.
        """
        ipcantberemovedfromvip = get_model('ip', 'IpCantBeRemovedFromVip')

        id_vip = self.id
        id_ipv4 = self.ipv4
        id_ipv6 = self.ipv6

        if self.created:
            raise exceptions.VipConstraintCreated(id_vip)

        self.delete_pools_related()

        self.delete()

        # delete Ipv4
        if self.ipv4 and bypass_ipv4 is False:

            if not self._is_ipv4_in_use(id_ipv4, id_vip):
                try:
                    self.ipv4.delete_v3()
                except ipcantberemovedfromvip:
                    self.log.info(
                        'Tried to delete Ipv4, because assoc with in more Vips.')
                    pass
                except Exception, e:
                    self.log.error(e)
                    raise Exception('Error to delete Ipv4: %s.', e)

        # delete Ipv6
        if self.ipv6 and bypass_ipv6 is False:
            if not self._is_ipv6_in_use(id_ipv6, id_vip):
                try:
                    self.ipv6.delete_v3()
                except ipcantberemovedfromvip:
                    self.log.info(
                        'Tried to delete Ipv6, because assoc with in more Vips.')
                    pass
                except Exception, e:
                    self.log.error(e)
                    raise Exception('Error to delete Ipv4: %s.', e)

        # sync with old tables
        if sync:
            syncs.delete_old(id_vip)

    def _is_ipv4_in_use(self, ipv4, id_vip=None):
        id_vip = id_vip if id_vip else self.id
        spm_model = get_model('requisicaovips', 'ServerPoolMember')
        vp_model = get_model('api_vip_request', 'VipRequest')

        is_in_use = True

        pm_count = spm_model.objects.filter(ip=ipv4).exclude(
            server_pool__vipporttopool__requisicao_vip__id=self.id
        ).count()

        vip_count = vp_model.objects.filter(
            ipv4=ipv4
        ).exclude(pk=id_vip).count()

        if vip_count == 0 and pm_count == 0:
            is_in_use = False

        return is_in_use

    def _is_ipv6_in_use(self, ipv6, id_vip=None):
        id_vip = id_vip if id_vip else self.id
        spm_model = get_model('requisicaovips', 'ServerPoolMember')
        vp_model = get_model('api_vip_request', 'VipRequest')

        is_in_use = True

        pm_count = spm_model.objects.filter(ipv6=ipv6).exclude(
            server_pool__vipporttopool__requisicao_vip__ipv6=self.id
        ).count()

        vip_count = vp_model.objects.filter(
            ipv6=ipv6
        ).exclude(pk=id_vip).count()

        if vip_count == 0 and pm_count == 0:
            is_in_use = False

        return is_in_use

    @classmethod
    def get_pool_related(cls, id_vip):
        sp_model = get_model('requisicaovips', 'ServerPool')

        pools = sp_model.objects.filter(
            viprequestportpool__vip_request_port__vip_request__id=id_vip
        ).distinct()

        return pools

    def delete_pools_related(self):

        # Pools related with vip and was not created
        pools = self.get_pool_related(
            self.id
        ).filter(pool_created=False)
        # Pools assoc with others Vips
        pools_assoc = pools.exclude(
            viprequestportpool__vip_request_port__vip_request__id=self.id
        )
        # Remove pool not created and not assoc with others vips
        for pool in pools:
            if pool not in pools_assoc:
                pool.delete()


class VipRequestOptionVip(BaseModel):

    log = logging.getLogger('VipRequestOptionVip')

    id = models.AutoField(
        primary_key=True,
        db_column='id'
    )

    vip_request = models.ForeignKey(
        VipRequest,
        db_column='id_vip_request',
    )

    optionvip = models.ForeignKey(
        'requisicaovips.OptionVip',
        db_column='id_opcoesvip',
    )

    @cached_property
    def traffic_return(self):
        opt = self.optionvip \
            if self.optionvip.tipo_opcao == 'Retorno de trafego' \
            else None
        return opt

    @cached_property
    def cache_group(self):
        opt = self.optionvip \
            if self.optionvip.tipo_opcao == 'cache' \
            else None
        return opt

    @cached_property
    def persistence(self):
        opt = self.optionvip \
            if self.optionvip.tipo_opcao == 'Persistencia' \
            else None
        return opt

    @cached_property
    def timeout(self):
        opt = self.optionvip \
            if self.optionvip.tipo_opcao == 'timeout' \
            else None
        return opt

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
            cls.log.error(
                u'vip request option vip not found. pk {}'.format(id))
            raise exceptions.VipRequestOptionVipNotFoundError(id)
        except OperationalError, e:
            cls.log.error(u'Lock wait timeout exceeded.')
            raise OperationalError(
                e, u'Lock wait timeout exceeded; try restarting transaction')
        except Exception, e:
            cls.log.error(u'Failure to search the option vip.')
            raise exceptions.VipRequestOptionVipError(
                e, u'Failure to search the vip request option vip.')

    @classmethod
    def get_by_kind(cls, vip_request_id, kind):
        """"Get Vip Request Option Vip by Vip Request and kind.

        @return: Vip Request Option Vip.

        @raise VipRequestOptionVipNotFoundError: Vip Request Option Vip not registered.
        @raise VipRequestOptionVipError: Failed to search for the Vip Request Option Vip.
        @raise OperationalError: Lock wait timeout exceeded.
        """
        try:
            return VipRequestOptionVip.objects.get(
                vip_request_id=vip_request_id, optionvip__tipo_opcao=kind)
        except ObjectDoesNotExist, e:
            cls.log.error(
                u'Vip request option vip not found. Vip {} '
                u'kind {}'.format(vip_request_id, kind))
            raise exceptions.VipRequestOptionVipNotFoundError(id)
        except OperationalError, e:
            cls.log.error(u'Lock wait timeout exceeded.')
            raise OperationalError(
                e, u'Lock wait timeout exceeded; try restarting transaction')
        except Exception, e:
            cls.log.error(u'Failure to search the option vip.')
            raise exceptions.VipRequestOptionVipError(
                e, u'Failure to search the vip request option vip.')


class VipRequestPort(BaseModel):

    log = logging.getLogger('VipRequestPort')

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

    @cached_property
    def pools(self):
        pools = self.viprequestportpool_set.all()
        return pools

    @cached_property
    def options(self):
        options = self.viprequestportoptionvip_set.all()
        return options

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
            raise exceptions.VipRequestPortError(
                e, u'Failure to search the vip request port.')


class VipRequestPortOptionVip(BaseModel):

    log = logging.getLogger('VipRequestPortOptionVip')

    id = models.AutoField(
        primary_key=True,
        db_column='id'
    )

    vip_request_port = models.ForeignKey(
        VipRequestPort,
        db_column='id_vip_request_port',
    )

    optionvip = models.ForeignKey(
        'requisicaovips.OptionVip',
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
            cls.log.error(
                u'vip request port option vip not found. pk {}'.format(id))
            raise exceptions.VipRequestPortOptionVipNotFoundError(id)
        except OperationalError, e:
            cls.log.error(u'Lock wait timeout exceeded.')
            raise OperationalError(
                e, u'Lock wait timeout exceeded; try restarting transaction')
        except Exception, e:
            cls.log.error(u'Failure to search the option vip.')
            raise exceptions.VipRequestPortOptionVipError(
                e, u'Failure to search the vip request port option vip.')


class VipRequestPortPool(BaseModel):

    log = logging.getLogger('VipRequestPortPool')

    id = models.AutoField(
        primary_key=True,
        db_column='id'
    )

    vip_request_port = models.ForeignKey(
        VipRequestPort,
        db_column='id_vip_request_port',
    )

    optionvip = models.ForeignKey(
        'requisicaovips.OptionVip',
        db_column='id_opcoesvip',
    )

    server_pool = models.ForeignKey(
        'requisicaovips.ServerPool',
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

    @cached_property
    def l7_rule(self):
        return self.optionvip

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
            raise exceptions.VipRequestPortPoolError(
                e, u'Failure to search the vip request port pool.')


class VipRequestDSCP(BaseModel):

    log = logging.getLogger('VipRequestDSCP')

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
            raise exceptions.VipRequestDSCPError(
                e, u'Failure to search the vip request dscp.')


class VipRequestGroupPermission(BaseModel):

    log = logging.getLogger('VipRequestGroupPermission')

    id = models.AutoField(
        primary_key=True,
        db_column='id'
    )
    user_group = models.ForeignKey(
        'grupo.UGrupo',
        db_column='id_user_group'
    )
    vip_request = models.ForeignKey(
        VipRequest,
        db_column='id_vip_request'
    )
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
            cls.log.error(
                u'vip request group permission not found. pk {}'.format(id))
            raise exceptions.VipRequestGroupPermissionNotFoundError(id)
        except OperationalError, e:
            cls.log.error(u'Lock wait timeout exceeded.')
            raise OperationalError(
                e, u'Lock wait timeout exceeded; try restarting transaction')
        except Exception, e:
            cls.log.error(u'Failure to search the option vip.')
            raise exceptions.VipRequestGroupPermissionError(
                e, u'Failure to search the vip request group permission.')
