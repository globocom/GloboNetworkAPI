
import itertools
import logging

import bigsuds

from networkapi.plugins import exceptions as base_exceptions
from networkapi.plugins.F5 import monitor, node, pool, poolmember,\
    rule, util, virtualserver
from networkapi.plugins.F5.util import logger

from ..base import BasePlugin

log = logging.getLogger(__name__)


class Generic(BasePlugin):

    #######################################
    # VIP
    #######################################
    @logger
    @util.connection
    def delete_vip(self, vips):
        pools_del = list()
        tratado = util.trata_param_vip(vips)
        vts = virtualserver.VirtualServer(self._lb)
        try:
            self._lb._channel.System.Session.start_transaction()
            if tratado.get('vips_filter'):
                vps_names = [vp['name'] for vp in tratado.get('vips_filter')]
                vts.delete(vps_names=vps_names)

                rule_l7 = ['{}_RULE_L7'.format(vp['name'])
                           for vp in tratado.get('vips_filter') if vp.get('pool_l7')]
                if rule_l7:
                    rl = rule.Rule(self._lb)
                    rl.delete(rule_names=rule_l7)

            # CACHE
            if tratado.get('vips_cache_filter'):
                vps_names = [vp['name'] for vp in tratado.get('vips_cache_filter')]
                vts.delete(vps_names=vps_names)
        except Exception, e:
            log.error(e)
            self._lb._channel.System.Session.rollback_transaction()
            raise e
        else:
            self._lb._channel.System.Session.submit_transaction()

            if tratado.get('pool_filter_created'):
                try:
                    self.__delete_pool({'pools': tratado.get('pool_filter_created')})
                except Exception, e:
                    if 'cannot be deleted because it is in use by a Virtual Server' in str(e.message):
                        log.warning('"Pool cannot be deleted because it is in use by a Virtual Server"')
                        pass
                    else:
                        raise e
                else:
                    pools_del = [server_pool.get('id') for server_pool in tratado.get('pool_filter_created')]

        return pools_del

    @logger
    @util.connection
    def create_vip(self, vips):
        tratado = util.trata_param_vip(vips)
        vts = virtualserver.VirtualServer(self._lb)

        # vip create
        if tratado.get('pool_filter'):
            self.__create_pool({'pools': tratado.get('pool_filter')})
        try:
            if tratado.get('vips_filter'):
                vts.create(vips=tratado.get('vips_filter'))
        except Exception, e:
            log.error(e)

            if tratado.get('pool_filter'):
                self.__delete_pool({'pools': tratado.get('pool_filter')})
            raise base_exceptions.CommandErrorException(e)

        else:

            # cache layer
            try:
                if tratado.get('vips_cache_filter'):
                    vts.create(vips=tratado.get('vips_cache_filter'))
            except Exception, e:
                log.error(e)

                # rollback vip create
                try:
                    if tratado.get('vips_filter'):
                        vps_names = [vp['name'] for vp in tratado.get('vips_filter')]
                        vts.delete(vps_names=vps_names)
                except Exception, e:
                    log.error(e)
                    raise base_exceptions.CommandErrorException(e)
                else:
                    if tratado.get('pool_filter'):
                        self.__delete_pool({'pools': tratado.get('pool_filter')})

                raise base_exceptions.CommandErrorException(e)

    @logger
    @util.connection
    def update_vip(self, vips):
        tratado = util.trata_param_vip(vips)
        vts = virtualserver.VirtualServer(self._lb)

        try:
            if tratado.get('vips_filter'):
                vts.update(vips=tratado.get('vips_filter'))
        except Exception, e:
            log.error(e)
            raise base_exceptions.CommandErrorException(e)

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

            pl.set_monitor_association(monitor_associations=monitor_associations)

            pl.set_service_down_action(
                names=pls['pools_names'],
                actions=pls['pools_actions'])

            plm = poolmember.PoolMember(self._lb)

            plm.set_connection_limit(
                names=pls['pools_names'],
                members=pls['pools_members']['members'],
                connection_limit=pls['pools_members']['limit'])

            plm.set_priority(
                names=pls['pools_names'],
                members=pls['pools_members']['members'],
                priority=pls['pools_members']['priority'])

            plm.set_member_description(
                names=pls['pools_names'],
                members=pls['pools_members']['members'],
                description=pls['pools_members']['description'])

            plm.set_states(
                names=pls['pools_names'],
                members=pls['pools_members']['members'],
                monitor_state=pls['pools_members']['monitor'],
                session_state=pls['pools_members']['session'])

        except Exception, e:
            log.error(e)
            self._lb._channel.System.Session.rollback_transaction()
            template_names = [m for m in list(itertools.chain(*[m['monitor_rule']['monitor_templates'] for m in monitor_associations])) if 'MONITOR' in m]
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
                    nd.set_monitor_rule(monitor_associations=monitor_associations_nodes)
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
        monitor_associations_old = pl.get_monitor_association(names=pls['pools_names'])

        # creates templates
        monitor_associations, monitor_associations_nodes, templates_extra = mon.prepare_template(
            names=pls['pools_names'],
            members=pls['pools_members']['members'],
            healthcheck=pls['pools_healthcheck']
        )

        mon.create_template(templates_extra=templates_extra)

        try:
            self._lb._channel.System.Session.start_transaction()

            pl.set_monitor_association(monitor_associations=monitor_associations)

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

            plm.set_member_description(
                names=pls['pools_names'],
                members=pls['pools_members']['members'],
                description=pls['pools_members']['description'])

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
                    nd.set_monitor_rule(monitor_associations=monitor_associations_nodes)

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
            self._lb._channel.System.Session.start_transaction()
            monitor_associations = pl.get_monitor_association(names=pls['pools_names'])
            pl.remove_monitor_association(names=pls['pools_names'])
        except Exception, e:
            log.error(e)
            self._lb._channel.System.Session.rollback_transaction()
            raise base_exceptions.CommandErrorException(e)
        else:
            self._lb._channel.System.Session.submit_transaction()

            try:
                self._lb._channel.System.Session.start_transaction()
                pl.delete(names=pls['pools_names'])
            except Exception, e:
                log.error(e)
                self._lb._channel.System.Session.rollback_transaction()
                pl.set_monitor_association(monitor_associations=monitor_associations)
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
