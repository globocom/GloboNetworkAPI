# -*- coding: utf-8 -*-
import itertools
import logging

import bigsuds

from ..base import BasePlugin
from networkapi.plugins import exceptions as base_exceptions
from networkapi.plugins.F5 import monitor
from networkapi.plugins.F5 import node
from networkapi.plugins.F5 import pool
from networkapi.plugins.F5 import poolmember
from networkapi.plugins.F5 import rule
from networkapi.plugins.F5 import util
from networkapi.plugins.F5 import virtualserver
from networkapi.plugins.F5.util import logger

log = logging.getLogger(__name__)


class Generic(BasePlugin):

    #######################################
    # VIP
    #######################################
    @logger
    def get_name_eqpt(self, obj, port):
        address = obj.ipv4.ip_formated \
            if obj.ipv4 else obj.ipv6.ip_formated

        name_vip = 'VIP%s_%s_%s' % (obj.id, address, port)
        name_vip = str.replace(str(name_vip), ':', '.')

        return name_vip

    @logger
    @util.connection
    def delete_vip(self, vips):
        tratado = util.trata_param_vip(vips)
        dict_vip = {
            'vips': tratado.get('vips_filter'),
            'vips_cache': tratado.get('vips_cache_filter'),
            'pool_created': tratado.get('pool_filter_created')
        }
        pools_del = self._delete_vip(dict_vip)

        return pools_del

    @logger
    def _delete_vip(self, tratado):

        pools_del = list()
        vts = virtualserver.VirtualServer(self._lb)
        try:
            self._lb._channel.System.Session.start_transaction()
            if tratado.get('vips'):
                vps_names = [vp['name'] for vp in tratado.get('vips')]
                vts.delete(vps_names=vps_names)

                rule_l7 = ['{}_RULE_L7'.format(vp['name'])
                           for vp in tratado.get('vips') if vp.get('pool_l7')]
                if rule_l7:
                    rl = rule.Rule(self._lb)
                    rl.delete(rule_names=rule_l7)

            # CACHE
            if tratado.get('vips_cache'):
                vps_names = [vp['name'] for vp in tratado.get('vips_cache')]
                vts.delete(vps_names=vps_names)
        except Exception, e:
            log.error(e)
            self._lb._channel.System.Session.rollback_transaction()
            raise e
        else:
            self._lb._channel.System.Session.submit_transaction()

            if tratado.get('pool_created'):
                for server_pool in tratado.get('pool_created'):
                    if self._delete_pool_by_pass(server_pool):
                        pools_del.append(server_pool.get('id'))

        return pools_del

    @logger
    @util.connection
    def create_vip(self, vips):
        tratado = util.trata_param_vip(vips)
        dict_vip = {
            'vips_cache': tratado.get('vips_cache_filter'),
            'vips': tratado.get('vips_filter'),
            'pool': tratado.get('pool_filter')
        }
        pools_ins = self._create_vip(dict_vip)
        return pools_ins

    @logger
    def _create_vip(self, tratado):
        pools_ins = list()
        vts = virtualserver.VirtualServer(self._lb)
        # vip create
        if tratado.get('pool'):
            self.__create_pool({'pools': tratado.get('pool')})
            pools_ins = [server_pool.get('id')
                         for server_pool in tratado.get('pool')]
        try:
            if tratado.get('vips'):
                vts.create(vips=tratado.get('vips'))
        except Exception, e:
            log.error(e)

            if tratado.get('pool'):
                self.__delete_pool({'pools': tratado.get('pool')})
            raise base_exceptions.CommandErrorException(e)

        else:

            # cache layer
            try:
                if tratado.get('vips_cache'):
                    vts.create(vips=tratado.get('vips_cache'))
            except Exception, e:
                log.error(e)

                # rollback vip create
                try:
                    if tratado.get('vips'):
                        vps_names = [vp['name'] for vp in tratado.get('vips')]
                        vts.delete(vps_names=vps_names)
                except Exception, e:
                    log.error(e)
                    raise base_exceptions.CommandErrorException(e)
                else:
                    if tratado.get('pool'):
                        self.__delete_pool({'pools': tratado.get('pool')})

                raise base_exceptions.CommandErrorException(e)
        return pools_ins

    @logger
    @util.connection
    def update_vip(self, vips):

        pools_ins = list()
        pools_del = list()

        tratado = util.trata_param_vip(vips)
        vts = virtualserver.VirtualServer(self._lb)

        dict_create_vip = {
            'vips_cache': tratado.get('vips_cache_filter_to_insert'),
            'vips': tratado.get('vips_filter_to_insert'),
            'pool': tratado.get('pool_filter_to_insert')
        }
        dict_delete_vip = {
            'vips_cache': tratado.get('vips_cache_filter_to_delete'),
            'vips': tratado.get('vips_filter_to_delete'),
            'pool_created': list()
        }

        # delete ports
        try:

            log.info('try delete ports')
            pools_del = self._delete_vip(dict_delete_vip)
            vts = virtualserver.VirtualServer(self._lb)

        except Exception, e:

            log.error('error to delete ports')
            log.error(e)

            # rollback delete of ports
            log.info('rollback delete of ports')
            pools_del = self._delete_vip(dict_create_vip)

            raise base_exceptions.CommandErrorException(e)

        else:

            log.info('delete ports with success')

        # create new ports
        # create new pools(of new ports and old ports)
        try:

            log.info('try create ports')
            pools_ins = self._create_vip(dict_create_vip)

        except Exception, e:

            log.error('error to create new ports and new pools')
            log.error(e)
            raise base_exceptions.CommandErrorException(e)

        else:

            log.info('success create ports')

        # update vips(old ports)
        try:

            log.info('try update vips')
            if tratado.get('vips_filter'):
                vts.update(vips=tratado.get('vips_filter'))

        except Exception, e:

            log.info('error update vips')
            log.error(e)

            # rollback create port
            log.info('rollback create port')
            self._create_vip(dict_delete_vip)

            # rollback delete port
            log.info('rollback delete port')
            self._delete_vip(dict_create_vip)

            raise base_exceptions.CommandErrorException(e)

        else:
            # delete pools that not were deleted in first call
            if tratado.get('pool_filter_to_delete'):
                log.info('try delete pools that not were deleted in first call')
                for server_pool in tratado.get('pool_filter_to_delete'):
                    if self._delete_pool_by_pass(server_pool):
                        pools_del.append(server_pool.get('id'))

            log.info('update vips with success')

        return pools_ins, pools_del

    @logger
    @util.connection
    def partial_update_vip(self, vips):

        tratado = util.trata_param_vip(vips)
        vts = virtualserver.VirtualServer(self._lb)
        try:

            log.info('try update vips')
            if tratado.get('vips_filter'):
                vts.partial_update(vips=tratado.get('vips_filter'))
        except Exception, e:

            log.info('error update vips')
            log.error(e)

            raise base_exceptions.CommandErrorException(e)

        else:

            log.info('update vips with success')

        return [], []

    @logger
    def _delete_pool_by_pass(self, server_pool):
        try:
            self.__delete_pool({'pools': [server_pool]})
        except Exception, e:
            if 'cannot be deleted because it is in use by a Virtual Server' in str(e.message):
                log.warning(
                    'Pool cannot be deleted because it is in use by a Virtual Server')
                pass
            elif 'is referenced by one or more virtual servers' in str(e.message):
                log.warning(
                    'Pool cannot be deleted because it is referenced by one or more virtual servers')
                pass
            elif 'is referenced by one or more rules' in str(e.message):
                log.warning(
                    'Pool cannot be deleted because is referenced by one or more rules')
                pass
            else:
                raise e

            return False
        return True

    #######################################
    # POOLMEMBER
    #######################################
    @logger
    @util.transation
    def set_state_member(self, pools):

        pls = util.trata_param_pool(pools)

        plm = poolmember.PoolMember(self._lb)

        plm.set_states(
            names=pls['pools_names'],
            members=pls['pools_members']['members'],
            monitor_state=pls['pools_members']['monitor'],
            session_state=pls['pools_members']['session'])

    @logger
    @util.transation
    def set_connection_limit_member(self, pools):

        pls = util.trata_param_pool(pools)

        plm = poolmember.PoolMember(self._lb)
        plm.setConnectionLimit(
            names=pls['pools_names'],
            members=pls['pools_members']['members'],
            connection_limit=pls['pools_members']['limit'])

    @logger
    @util.transation
    def set_priority_member(self, pools):

        pls = util.trata_param_pool(pools)

        plm = poolmember.PoolMember(self._lb)
        plm.setPriority(
            names=pls['pools_names'],
            members=pls['pools_members']['members'],
            priority=pls['pools_members']['priority'])

    @logger
    @util.connection_simple
    def get_state_member(self, pools):
        pls = util.trata_param_pool(pools)

        plm = poolmember.PoolMember(self._lb)
        return plm.get_states(
            names=pls['pools_names'],
            members=pls['pools_members']['members'])

    @logger
    @util.transation
    def create_member(self, pools):

        pls = util.trata_param_pool(pools)

        plm = poolmember.PoolMember(self._lb)
        return plm.create(
            names=pls['pools_names'],
            members=pls['pools_members']['members'])

    @logger
    @util.transation
    def remove_member(self, pools):

        pls = util.trata_param_pool(pools)

        plm = poolmember.PoolMember(self._lb)
        return plm.remove(
            names=pls['pools_names'],
            members=pls['pools_members']['members'])

    #######################################
    # POOL
    #######################################
    @logger
    @util.connection
    def create_pool(self, pools):
        self.__create_pool(pools)

    @logger
    def __create_pool(self, pools):

        monitor_associations = []
        pls = util.trata_param_pool(pools)

        mon = monitor.Monitor(self._lb)

        monitor_associations, monitor_associations_nodes, templates_extra = mon.prepare_template(
            names=pls['pools_names'],
            members=pls['pools_members']['members'],
            healthcheck=pls['pools_healthcheck']
        )

        mon.create_template(templates_extra=templates_extra)

        try:
            self._lb._channel.System.Session.start_transaction()

            pl = pool.Pool(self._lb)

            pl.create(
                names=pls['pools_names'],
                lbmethod=pls['pools_lbmethod'],
                members=pls['pools_members']['members'])

            pl.set_monitor_association(
                monitor_associations=monitor_associations)

            pl.set_service_down_action(
                names=pls['pools_names'],
                actions=pls['pools_actions'])

            pl.set_minimum_active_member(
                names=pls['pools_names'])

            plm = poolmember.PoolMember(self._lb)

            plm.set_connection_limit(
                names=pls['pools_names'],
                members=pls['pools_members']['members'],
                connection_limit=pls['pools_members']['limit'])

            plm.set_priority(
                names=pls['pools_names'],
                members=pls['pools_members']['members'],
                priority=pls['pools_members']['priority'])

            # plm.set_member_description(
            #     names=pls['pools_names'],
            #     members=pls['pools_members']['members'],
            #     description=pls['pools_members']['description'])

            plm.set_states(
                names=pls['pools_names'],
                members=pls['pools_members']['members'],
                monitor_state=pls['pools_members']['monitor'],
                session_state=pls['pools_members']['session'])

        except Exception, e:
            log.error(e)
            self._lb._channel.System.Session.rollback_transaction()
            template_names = [m for m in list(itertools.chain(
                *[m['monitor_rule']['monitor_templates'] for m in monitor_associations])) if 'MONITOR' in m]
            if template_names != []:
                mon.delete_template(
                    template_names=template_names
                )
            raise base_exceptions.CommandErrorException(e)
        else:
            self._lb._channel.System.Session.submit_transaction()

            try:
                if monitor_associations_nodes.get('nodes'):
                    nd = node.Node(self._lb)
                    nd.set_monitor_rule(
                        monitor_associations=monitor_associations_nodes)
            except bigsuds.OperationFailed:
                pass

    @logger
    @util.connection
    def update_pool(self, pools):
        self.__update_pool(pools)

    @logger
    def __update_pool(self, pools):
        monitor_associations = []
        pls = util.trata_param_pool(pools)

        pl = pool.Pool(self._lb)
        mon = monitor.Monitor(self._lb)

        # get template currents
        monitor_associations_old = pl.get_monitor_association(
            names=pls['pools_names'])

        # creates templates
        monitor_associations, monitor_associations_nodes, templates_extra = mon.prepare_template(
            names=pls['pools_names'],
            members=pls['pools_members']['members'],
            healthcheck=pls['pools_healthcheck']
        )

        mon.create_template(templates_extra=templates_extra)

        try:
            self._lb._channel.System.Session.start_transaction()

            pl.set_monitor_association(
                monitor_associations=monitor_associations)

            pl.set_lb_method(
                names=pls['pools_names'],
                lbmethod=pls['pools_lbmethod'])

            pl.set_service_down_action(
                names=pls['pools_names'],
                actions=pls['pools_actions'])

            plm = poolmember.PoolMember(self._lb)

            if pls['pools_members']['members_remove']:
                plm.remove(
                    names=pls['pools_names'],
                    members=pls['pools_members']['members_remove'])

            if pls['pools_members']['members_new']:
                plm.create(
                    names=pls['pools_names'],
                    members=pls['pools_members']['members_new'])

            plm.set_connection_limit(
                names=pls['pools_names'],
                members=pls['pools_members']['members'],
                connection_limit=pls['pools_members']['limit'])

            plm.set_priority(
                names=pls['pools_names'],
                members=pls['pools_members']['members'],
                priority=pls['pools_members']['priority'])

            # plm.set_member_description(
            #     names=pls['pools_names'],
            #     members=pls['pools_members']['members'],
            #     description=pls['pools_members']['description'])

            plm.set_states(
                names=pls['pools_names'],
                members=pls['pools_members']['members'],
                monitor_state=pls['pools_members']['monitor'],
                session_state=pls['pools_members']['session'])

        except Exception, e:
            log.error(e)
            self._lb._channel.System.Session.rollback_transaction()

            # delete templates created
            template_names = [m for m in list(
                itertools.chain(
                    *[m['monitor_rule']['monitor_templates'] for m in monitor_associations])
            ) if 'MONITOR' in m]
            if template_names:
                mon.delete_template(
                    template_names=template_names
                )
            raise base_exceptions.CommandErrorException(e)
        else:
            self._lb._channel.System.Session.submit_transaction()

            try:

                if monitor_associations_nodes.get('nodes'):
                    nd = node.Node(self._lb)
                    nd.set_monitor_rule(
                        monitor_associations=monitor_associations_nodes)

                if pls['pools_confirm']['pools_names']:
                    plm.set_member_monitor_state(
                        names=pls['pools_confirm']['pools_names'],
                        members=pls['pools_confirm']['members'],
                        monitor_state=pls['pools_confirm']['monitor'])
            except bigsuds.OperationFailed:
                pass

            # delete templates old
            try:
                template_names = [m for m in list(
                    itertools.chain(*[m['monitor_rule']['monitor_templates'] for m in monitor_associations_old])) if 'MONITOR' in m]
                if template_names:
                    mon.delete_template(template_names=template_names)
            except bigsuds.OperationFailed:
                pass

    @logger
    @util.connection
    def delete_pool(self, pools):
        self.__delete_pool(pools)

    @logger
    def __delete_pool(self, pools):

        pls = util.trata_param_pool(pools)

        pl = pool.Pool(self._lb)
        mon = monitor.Monitor(self._lb)

        try:
            monitor_associations = pl.get_monitor_association(
                names=pls['pools_names'])
        except Exception, e:
            log.error(e)
            raise base_exceptions.CommandErrorException(e)
        else:

            try:
                self._lb._channel.System.Session.start_transaction()
                pl.delete(names=pls['pools_names'])
            except Exception, e:
                log.error(e)
                self._lb._channel.System.Session.rollback_transaction()
                raise base_exceptions.CommandErrorException(e)
            else:
                self._lb._channel.System.Session.submit_transaction()
                try:
                    template_names = [m for m in list(
                        itertools.chain(
                            *[m['monitor_rule']['monitor_templates'] for m in monitor_associations])) if 'MONITOR' in m]
                    if template_names:
                        mon.delete_template(template_names=template_names)
                except bigsuds.OperationFailed:
                    pass
