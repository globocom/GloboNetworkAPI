# -*- coding: utf-8 -*-
import logging
from itertools import chain

from _mysql_exceptions import OperationalError
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models import get_model
from django.db.models import Q

from networkapi.admin_permission import AdminPermission
from networkapi.api_pools import exceptions as exceptions_pool
from networkapi.api_rest.exceptions import ValidationAPIException
from networkapi.api_vip_request import exceptions
from networkapi.api_vip_request import syncs
from networkapi.models.BaseModel import BaseModel
from networkapi.plugins.factory import PluginFactory
from networkapi.util.decorators import cached_property
from networkapi.util.geral import get_app


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

    def __str__(self):
        return str(self.id)

    @cached_property
    def dscp(self):
        try:
            dscp = self.viprequestdscp_set.get()
            return dscp.dscp
        except ObjectDoesNotExist:
            return None

    @cached_property
    def equipments(self):
        if self.ipv4 and not self.ipv6:
            eqpts = self.ipv4.ipequipamento_set.all()\
                .prefetch_related('equipamento')
        elif self.ipv6 and not self.ipv4:
            eqpts = self.ipv6.ipv6equipament_set.all()\
                .prefetch_related('equipamento')
        elif self.ipv4 and self.ipv6:
            eqpts_v4 = self.ipv4.ipequipamento_set.all()\
                .prefetch_related('equipamento')
            eqpts_v6 = self.ipv6.ipv6equipament_set.all()\
                .prefetch_related('equipamento')
            eqpts = list(chain(eqpts_v4, eqpts_v6))

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
        ogp_models = get_app('api_ogp', 'models')
        perms = ogp_models.ObjectGroupPermission\
            .get_by_object(self.id, AdminPermission.OBJ_TYPE_VIP)
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

    def _delete_pools_related(self):

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

    def get_dscp(self):
        reqvip_models = get_app('requisicaovips', 'models')

        members = reqvip_models.ServerPoolMember.objects.filter(
            server_pool__viprequestportpool__vip_request_port__vip_request__id=self.id)
        eqpts = [member.equipment.id for member in members]

        members = VipRequestDSCP.objects.filter(
            vip_request__viprequestport__viprequestportpool__server_pool__serverpoolmember__in=reqvip_models.ServerPoolMember.objects.filter(
                ip__ipequipamento__equipamento__in=eqpts
            )
        ).distinct().values('dscp')

        mb = [i.get('dscp') for i in members]
        perm = range(3, 64)
        perm_new = list(set(perm) - set(mb))
        if perm_new:
            return perm_new[0]
        else:
            raise Exception(
                'Can\'t use pool because pool members have dscp is sold out')

    def _create_option(self, options):
        """create options"""

        reqvip_models = get_app('requisicaovips', 'models')

        for option in options:
            opt = VipRequestOptionVip()
            opt_map = {
                'vip_request': self.id,
                'optionvip': option
            }
            opt.create_v3(opt_map)

        # DSCP
        try:
            dsrl3 = reqvip_models.OptionVip.objects.get(
                nome_opcao_txt='DSRL3',
                tipo_opcao='Retorno de trafego'
            )
        except ObjectDoesNotExist:
            pass
        else:
            if dsrl3.id in options:
                vip_dscp = VipRequestDSCP()
                dscp_map = {
                    'vip_request': self.id,
                    'dscp': self.get_dscp(),
                }
                vip_dscp.create_v3(dscp_map)

    def _delete_option(self, options):
        """Deletes options"""

        reqvip_models = get_app('requisicaovips', 'models')

        VipRequestOptionVip.objects.filter(
            vip_request=self.id,
            optionvip__in=options
        ).delete()

        # DSCP
        try:
            dsrl3 = reqvip_models.OptionVip.objects.get(
                nome_opcao_txt='DSRL3',
                tipo_opcao='Retorno de trafego'
            )
        except ObjectDoesNotExist:
            pass
        else:
            if dsrl3.id in options:
                VipRequestDSCP.objects.filter(vip_request=self.id).delete()

    def validate_save(self, vip_request, permit_created=False):

        env_models = get_app('ambiente', 'models')
        reqvip_models = get_app('requisicaovips', 'models')

        has_identifier = VipRequest.objects.filter(
            environmentvip=vip_request['environmentvip']
        )

        # validate ipv4
        if vip_request['ipv4']:
            has_identifier = has_identifier.filter(ipv4=vip_request['ipv4'])

            vips = env_models.EnvironmentVip.objects.filter(
                networkipv4__ip=vip_request['ipv4']
            ).filter(
                id=vip_request['environmentvip']
            )
            if not vips:
                raise exceptions.IpNotFoundByEnvironment(
                    'Environment of Ip: %s is different of environment of vip '
                    'request: %s. Look the association of network of IP with '
                    'environment vip.' %
                    (vip_request['ipv4'], vip_request['name'])
                )

        # validate ipv6
        if vip_request['ipv6']:
            has_identifier = has_identifier.filter(ipv6=vip_request['ipv6'])
            vips = env_models.EnvironmentVip.objects.filter(
                networkipv6__ipv6=vip_request['ipv6']
            ).filter(
                id=vip_request['environmentvip']
            )
            if not vips:
                raise exceptions.IpNotFoundByEnvironment(
                    'Environment of Ip: %s is different of environment of vip '
                    'request: %s. Look the association of network of IP with '
                    'environment vip.' %
                    (vip_request['ipv6'], vip_request['name'])
                )

        # validate change info when vip created
        if vip_request.get('id'):
            vip = VipRequest.get_by_pk(vip_request.get('id'))
            if vip.created:
                if not permit_created:
                    raise exceptions.CreatedVipRequestValuesException()

                if vip.environmentvip_id != vip_request['environmentvip']:
                    raise exceptions.CreatedVipRequestValuesException(
                        'Environment vip of vip request id: %s' % (vip_request.get('id')))

                # cannot change ip
                if vip.ipv4:
                    if vip.ipv4.id != vip_request['ipv4']:
                        raise exceptions.CreatedVipRequestValuesException(
                            'Ipv4 of vip request id: %s' % (vip_request.get('id')))
                if vip.ipv6:
                    if vip.ipv6.id != vip_request['ipv6']:
                        raise exceptions.CreatedVipRequestValuesException(
                            'Ipv6 of vip request id: %s' % (vip_request.get('id')))

                # change traffic return
                options = [
                    op.optionvip.id for op in vip.viprequestoptionvip_set.all()]
                if vip_request['options']['traffic_return'] not in options:
                    raise exceptions.CreatedVipRequestValuesException(
                        'Traffic Return of vip request id: %s' % (vip_request.get('id')))

                for port in vip_request.get('ports'):
                    if port.get('id'):
                        # cannot change options of port

                        port_obj = vip.viprequestport_set.get(
                            id=port.get('id'))

                        options_obj_l4 = port_obj.viprequestportoptionvip_set.filter(
                            optionvip=port.get('options').get('l4_protocol'))
                        options_obj_l7 = port_obj.viprequestportoptionvip_set.filter(
                            optionvip=port.get('options').get('l7_protocol'))

                        if not options_obj_l4 or not options_obj_l7:
                            raise exceptions.CreatedVipRequestValuesException(
                                'Options of port %s of vip request id: %s' % (port['port'], vip_request.get('id')))

            has_identifier = has_identifier.exclude(id=vip_request.get('id'))

        # validate option vip assoc with environment vip
        opts = list()
        for option in vip_request['options']:
            opt = dict()
            if option == 'cache_group' and vip_request['options'].get(option) is not None:
                opt['id'] = vip_request['options'].get(option)
                opt['tipo_opcao'] = 'cache'
            elif option == 'persistence' and vip_request['options'].get(option) is not None:
                opt['id'] = vip_request['options'].get(option)
                opt['tipo_opcao'] = 'Persistencia'
            elif option == 'traffic_return' and vip_request['options'].get(option) is not None:
                opt['id'] = vip_request['options'].get(option)
                opt['tipo_opcao'] = 'Retorno de trafego'
            elif option == 'timeout' and vip_request['options'].get(option) is not None:
                opt['id'] = vip_request['options'].get(option)
                opt['tipo_opcao'] = 'timeout'
            if opt:
                opts.append(opt)

        for opt in opts:
            try:
                option = reqvip_models.OptionVip.objects.get(
                    Q(**opt),
                    optionvipenvironmentvip__environment__id=vip_request[
                        'environmentvip']
                )
            except:
                raise Exception(
                    'Invalid option %s: %s, vip request: %s, because '
                    'environment vip is not associated to options or '
                    'not exists.' %
                    (opt['tipo_opcao'], opt['id'], vip_request['name'])
                )

        # validate pools associates
        for port in vip_request.get('ports'):

            opts = list()
            for option in port['options']:
                opt = dict()
                if option == 'l4_protocol' and port['options'].get(option) is not None:
                    opt['id'] = port['options'].get(option)
                    opt['tipo_opcao'] = 'l4_protocol'
                elif option == 'l7_protocol' and port['options'].get(option) is not None:
                    opt['id'] = port['options'].get(option)
                    opt['tipo_opcao'] = 'l7_protocol'
                if opt:
                    opts.append(opt)

            for opt in opts:
                try:
                    option = reqvip_models.OptionVip.objects.get(
                        Q(**opt),
                        optionvipenvironmentvip__environment__id=vip_request[
                            'environmentvip']
                    )
                except:
                    raise ValidationAPIException(
                        u'Invalid option %s: %s, port: %s, vip request: %s, '
                        'because environmentvip is not associated to options '
                        'or not exists.' % (
                            opt['tipo_opcao'], opt['id'],
                            port['port'], vip_request['name']
                        )
                    )

            dsrl3 = reqvip_models.OptionVip.objects.filter(
                nome_opcao_txt='DSRL3',
                tipo_opcao='Retorno de trafego',
                id=vip_request['options']['traffic_return'],
            )

            # validate dsrl3: 1 pool by port
            if dsrl3 and len(port['pools']) > 1:
                raise ValidationAPIException(
                    u'Vip %s has DSRL3 and can not to have L7' % (
                        vip_request['name'])
                )

            count_l7_opt = 0
            for pool in port['pools']:

                # validate option vip(l7_rule) assoc with environment vip
                try:
                    l7_rule_opt = reqvip_models.OptionVip.objects.get(
                        id=pool['l7_rule'],
                        tipo_opcao='l7_rule',
                        optionvipenvironmentvip__environment__id=vip_request[
                            'environmentvip']
                    )
                except:
                    raise ValidationAPIException(
                        u'Invalid option l7_rule: %s, pool: %s, port: %s,'
                        'viprequest: %s, because environmentvip is not '
                        'associated to options or not exists' % (
                            pool['l7_rule'], pool['server_pool'],
                            port['port'], vip_request['name'])
                    )

                # control to validate l7_rule "default_vip" in one pool by port
                if l7_rule_opt.nome_opcao_txt == 'default_vip':
                    count_l7_opt += 1

                # validate dsrl3: pool assoc only vip and no l7 rules
                if dsrl3:
                    # Vip with dscp(dsrl3) cannot L7 rules
                    if l7_rule_opt.nome_opcao_txt != 'default_vip':
                        raise ValidationAPIException(
                            u'Option Vip of pool %s of Vip Request %s must be '
                            'default_vip' %
                            (pool['server_pool'], vip_request['name'])
                        )

                    pool_assoc_vip = reqvip_models.ServerPool()\
                        .get_vips_related(pool['server_pool'])
                    if vip_request.get('id'):
                        pool_assoc_vip = pool_assoc_vip.exclude(
                            id=vip_request.get('id'))

                    if pool_assoc_vip:
                        raise ValidationAPIException(
                            u'Pool %s must be associated to a only 1 vip '
                            'request, when vip request has dslr3 option' %
                            (pool['server_pool']))

                try:
                    sp = reqvip_models.ServerPool.objects.get(
                        id=pool['server_pool'])
                except Exception, e:
                    self.log.error(e)
                    raise exceptions_pool.PoolDoesNotExistException(
                        pool['server_pool'])

                # validate dsrl3: Pool must have same port of vip
                if dsrl3:
                    if int(sp.default_port) != int(port['port']):
                        raise ValidationAPIException(
                            u'Pool %s must have same port of vip %s' %
                            (pool['server_pool'], vip_request['name'])
                        )

                spms = reqvip_models.ServerPoolMember.objects.filter(
                    server_pool=pool['server_pool'])
                for spm in spms:
                    # validate dsrl3: Pool Members must have same port of vip
                    if dsrl3:
                        if int(spm.port_real) != int(port['port']):
                            ip_mb = spm.ip if spm.ip else spm.ipv6
                            raise ValidationAPIException(
                                u'Pool Member %s of Pool {} must have same '
                                'port of vip %s' % (
                                    ip_mb, pool['server_pool'],
                                    vip_request['name'])
                            )

                    if spm.ip:

                        vips = env_models.EnvironmentVip.objects.filter(
                            environmentenvironmentvip__environment__vlan__networkipv4__ip=spm.ip
                        ).filter(
                            id=vip_request['environmentvip']
                        )
                        if not vips:
                            raise exceptions.ServerPoolMemberDiffEnvironmentVipException(
                                spm.identifier)
                    if spm.ipv6:

                        vips = env_models.EnvironmentVip.objects.filter(
                            environmentenvironmentvip__environment__vlan__networkipv6__ipv6=spm.ipv6
                        ).filter(
                            id=vip_request['environmentvip']
                        )
                        if not vips:
                            raise exceptions.ServerPoolMemberDiffEnvironmentVipException(
                                spm.identifier)

            if count_l7_opt < 1:
                raise ValidationAPIException(
                    u'Port {} of Vip Request {} must have one pool with l7_rule equal "default_vip"'.format(
                        port['port'], vip_request['name'])
                )

            if count_l7_opt > 1:
                raise ValidationAPIException(
                    u'Port {} of Vip Request {} must have only pool with l7_rule equal "default_vip"'.format(
                        port['port'], vip_request['name'])
                )

    def create_v3(self, vip_map, user):
        """Creates Vip Request."""

        ip_models = get_app('ip', 'models')
        env_models = get_app('ambiente', 'models')
        reqvip_models = get_app('requisicaovips', 'models')

        ogp_models = get_app('api_ogp', 'models')

        self.validate_save(vip_map, permit_created=False)

        req = reqvip_models.RequisicaoVips()
        req.save()

        self.id = req.id
        self.name = vip_map.get('name')
        self.service = vip_map.get('service')
        self.business = vip_map.get('business')

        # Environment VIP
        self.environmentvip = env_models.EnvironmentVip\
            .get_by_pk(vip_map.get('environmentvip'))
        # IPv4
        if vip_map.get('ipv4'):
            self.ipv4 = ip_models.Ip.get_by_pk(vip_map.get('ipv4'))
        # IPv6
        if vip_map.get('ipv6'):
            self.ipv6 = ip_models.Ipv6.get_by_pk(vip_map.get('ipv6'))

        self.save()

        # Options VIP
        option_create = [int(vip_map['options'][key])
                         for key in vip_map['options']]
        self._create_option(option_create)

        # Ports
        for port in vip_map['ports']:
            pt = VipRequestPort()
            port['vip_request'] = self.id
            pt.create_v3(port)

        # Permissions
        perm = ogp_models.ObjectGroupPermission()
        perm.create_perms(vip_map, self.id, AdminPermission.OBJ_TYPE_VIP, user)

        # sync with old tables
        syncs.new_to_old(self)

    def update_v3(self, vip_map, user, permit_created=False):
        """Updates Vip Request."""

        ip_models = get_app('ip', 'models')
        env_models = get_app('ambiente', 'models')

        ogp_models = get_app('api_ogp', 'models')

        self.validate_save(vip_map, permit_created=permit_created)

        self.name = vip_map.get('name')
        self.service = vip_map.get('service')
        self.business = vip_map.get('business')

        # Environment VIP
        self.environmentvip = env_models.EnvironmentVip\
            .get_by_pk(vip_map.get('environmentvip'))
        # IPv4
        if vip_map.get('ipv4'):
            self.ipv4 = ip_models.Ip.get_by_pk(vip_map.get('ipv4'))
        # IPv6
        if vip_map.get('ipv6'):
            self.ipv6 = ip_models.Ipv6.get_by_pk(vip_map.get('ipv6'))

        self.save()

        option_ids = [int(option.optionvip.id)
                      for option in self.viprequestoptionvip_set.all()]
        options = [int(vip_map['options'][key])
                   for key in vip_map['options']]
        option_remove = list(set(option_ids) - set(options))
        option_create = list(set(options) - set(option_ids))

        self._create_option(option_create)
        self._delete_option(option_remove)

        # Ports
        for port in vip_map.get('ports'):
            try:
                pt = VipRequestPort.objects.get(
                    vip_request_id=self.id,
                    port=port['port'])
            except:
                pt = VipRequestPort()
                port['vip_request'] = self.id
                pt.create_v3(port)
            else:
                pt.update_v3(port)

        # Deletes ports
        ports_ids = [port.get('port') for port in vip_map.get('ports')]
        VipRequestPort.objects.filter(
            vip_request_id=self.id
        ).exclude(
            port__in=ports_ids
        ).delete()

        # Permissions

        perm = ogp_models.ObjectGroupPermission()
        perm.update_perms(vip_map, self.id, AdminPermission.OBJ_TYPE_VIP, user)

        # sync with old tables
        syncs.new_to_old(self)

    def delete_v3(self, bypass_ipv4=False, bypass_ipv6=False, sync=True):
        """Delete Vip Request.

        @raise VipConstraintCreated: Vip request can not be deleted
                                     because it is created in equipment.
        """

        ip_models = get_app('ip')
        ogp_models = get_app('api_ogp', 'models')

        id_vip = self.id
        id_ipv4 = self.ipv4
        id_ipv6 = self.ipv6

        if self.created:
            raise exceptions.VipConstraintCreated(id_vip)

        self._delete_pools_related()

        self.delete()

        # Deletes Permissions
        ogp_models.ObjectGroupPermission.objects.filter(
            object_type__name=AdminPermission.OBJ_TYPE_VIP,
            object_value=id_vip
        ).delete()

        # delete Ipv4
        if self.ipv4 and bypass_ipv4 is False:

            if not self._is_ipv4_in_use(id_ipv4, id_vip):
                try:
                    self.ipv4.delete_v3()
                except ip_models.IpCantBeRemovedFromVip:
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
                except ip_models.IpCantBeRemovedFromVip:
                    self.log.info(
                        'Tried to delete Ipv6, because assoc with in more Vips.')
                    pass
                except Exception, e:
                    self.log.error(e)
                    raise Exception('Error to delete Ipv6: %s.', e)

        # sync with old tables
        if sync:
            syncs.delete_old(id_vip)


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

    def create_v3(self, option_map):

        reqvip_models = get_app('requisicaovips', 'models')

        self.vip_request = VipRequest\
            .get_by_pk(option_map.get('vip_request'))
        self.optionvip = reqvip_models.OptionVip\
            .get_by_pk(option_map.get('optionvip'))
        self.save()


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

    def create_v3(self, vip_port_map):
        # save port

        facade_eqpt = get_app('api_equipment', 'facade')

        self.vip_request = VipRequest.get_by_pk(
            vip_port_map.get('vip_request'))
        self.port = vip_port_map.get('port')

        eqpts = facade_eqpt.get_eqpt_by_envvip(
            self.vip_request.environmentvip.id)
        if eqpts:
            plugin = PluginFactory.factory(eqpts[0])
            identifier = plugin.get_name_eqpt(
                self.vip_request, vip_port_map['port'])
            self.identifier = identifier

        self.save()

        # L4 Protocol
        opt = VipRequestPortOptionVip()
        opt_map = {
            'vip_request_port': self.id,
            'optionvip': vip_port_map['options']['l4_protocol']
        }
        opt.create_v3(opt_map)

        # L7 Protocol
        opt = VipRequestPortOptionVip()
        opt_map = {
            'vip_request_port': self.id,
            'optionvip': vip_port_map['options']['l7_protocol']
        }
        opt.create_v3(opt_map)

        # Pools
        for pool in vip_port_map.get('pools'):
            pool_map = {
                'vip_request_port': self.id,
                'server_pool': pool.get('server_pool'),
                'optionvip': pool.get('l7_rule'),
                'val_optionvip': pool.get('l7_value'),
                'order': pool.get('order')
            }
            pl = VipRequestPortPool()
            pl.create_v3(pool_map)

    def update_v3(self, vip_port_map):
        facade_eqpt = get_app('api_equipment', 'facade')

        if not self.identifier or self.port != vip_port_map['port']:
            eqpts = facade_eqpt\
                .get_eqpt_by_envvip(self.vip_request.environmentvip.id)
            if eqpts:
                plugin = PluginFactory.factory(eqpts[0])
                identifier = plugin.get_name_eqpt(
                    self.vip_request,
                    vip_port_map['port']
                )
                self.identifier = identifier

        self.save()

        # L4 Protocol
        try:
            opt = VipRequestPortOptionVip.objects.get(
                vip_request_port_id=self.id,
                optionvip_id=vip_port_map.get('options').get('l4_protocol'))
        except:
            opt = VipRequestPortOptionVip()
            opt_map = {
                'vip_request_port': self.id,
                'optionvip': vip_port_map['options']['l4_protocol']
            }
            opt.create_v3(opt_map)
        # L7 Protocol
        try:
            opt = VipRequestPortOptionVip.objects.get(
                vip_request_port_id=self.id,
                optionvip_id=vip_port_map.get('options').get('l7_protocol'))
        except:
            opt = VipRequestPortOptionVip()
            opt_map = {
                'vip_request_port': self.id,
                'optionvip': vip_port_map['options']['l7_protocol']
            }
            opt.create_v3(opt_map)

        # Deletes option by port
        VipRequestPortOptionVip.objects.filter(
            vip_request_port_id=self.id
        ).exclude(
            optionvip_id__in=[
                vip_port_map.get('options').get('l4_protocol'),
                vip_port_map.get('options').get('l7_protocol')]
        ).delete()

        # Pools
        pools = list()
        for pool in vip_port_map.get('pools'):
            pool_map = {
                'vip_request_port': self.id,
                'server_pool': pool.get('server_pool'),
                'optionvip': pool.get('l7_rule'),
                'val_optionvip': pool.get('l7_value'),
                'order': pool.get('order')
            }
            try:
                pl = VipRequestPortPool.objects.get(
                    vip_request_port=self.id,
                    id=pool.get('id'))
            except:
                pl = VipRequestPortPool()
                pl.create_v3(pool_map)
            else:
                pl.update_v3(pool_map)

            pools.append(pl.id)

        # Deletes pool by port
        VipRequestPortPool.objects.filter(
            vip_request_port=self.id
        ).exclude(
            id__in=pools
        ).delete()


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

    def create_v3(self, option_map):

        reqvip_models = get_app('requisicaovips', 'models')

        self.vip_request_port = VipRequestPort\
            .get_by_pk(option_map.get('vip_request_port'))
        self.optionvip = reqvip_models.OptionVip\
            .get_by_pk(option_map.get('optionvip'))

        self.save()


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

    def create_v3(self, pool_map):

        reqvip_models = get_app('requisicaovips', 'models')

        self.vip_request_port = VipRequestPort\
            .get_by_pk(pool_map.get('vip_request_port'))
        self.server_pool = reqvip_models.ServerPool\
            .get_by_pk(pool_map.get('server_pool'))
        self.optionvip = reqvip_models.OptionVip\
            .get_by_pk(pool_map.get('optionvip'))
        self.val_optionvip = pool_map.get('val_optionvip')
        self.order = pool_map.get('order')

        self.save()

    def update_v3(self, pool_map):

        reqvip_models = get_app('requisicaovips', 'models')

        self.server_pool = reqvip_models.ServerPool\
            .get_by_pk(pool_map.get('server_pool'))
        self.optionvip = reqvip_models.OptionVip\
            .get_by_pk(pool_map.get('optionvip'))
        self.val_optionvip = pool_map.get('val_optionvip')
        self.order = pool_map.get('order')

        self.save()


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

    def create_v3(self, dscp_map):

        self.vip_request = VipRequest\
            .get_by_pk(dscp_map.get('vip_request'))
        self.dscp = dscp_map.get('dscp')

        self.save()
