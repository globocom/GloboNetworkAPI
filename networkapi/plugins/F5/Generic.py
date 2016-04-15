import itertools
import logging

import bigsuds

from networkapi.plugins import exceptions as base_exceptions
from networkapi.plugins.F5 import monitor, pool, poolmember, util, virtualserver

from ..base import BasePlugin

log = logging.getLogger(__name__)


class Generic(BasePlugin):

    #######################################
    # VIP
    #######################################
    @util.connection
    def create_vip(self, vips):
        vps, pls = util.trata_param_vip(vips)

        if pls:
            self.__create_pool({'pools': pls})
        try:
            self._lb._channel.System.Session.start_transaction()
            vts = virtualserver.VirtualServer(self._lb)
            vts.create(vips=vps)
        except Exception, e:
            self._lb._channel.System.Session.rollback_transaction()
            raise Exception(e)
        else:
            self._lb._channel.System.Session.submit_transaction()

    #######################################
    # POOLMEMBER
    #######################################
    @util.transation
    def set_state_member(self, pools):

        pls = util.trata_param_pool(pools)

        plm = poolmember.PoolMember(self._lb)

        plm.set_states(
            names=pls['pools_names'],
            members=pls['pools_members']['members'],
            monitor_state=pls['pools_members']['monitor'],
            session_state=pls['pools_members']['session'])

    @util.transation
    def set_connection_limit_member(self, pools):

        pls = util.trata_param_pool(pools)

        plm = poolmember.PoolMember(self._lb)
        plm.setConnectionLimit(
            names=pls['pools_names'],
            members=pls['pools_members']['members'],
            connection_limit=pls['pools_members']['limit'])

    @util.transation
    def set_priority_member(self, pools):

        pls = util.trata_param_pool(pools)

        plm = poolmember.PoolMember(self._lb)
        plm.setPriority(
            names=pls['pools_names'],
            members=pls['pools_members']['members'],
            priority=pls['pools_members']['priority'])

    @util.transation
    def get_state_member(self, pools):
        pls = util.trata_param_pool(pools)

        plm = poolmember.PoolMember(self._lb)
        return plm.get_states(
            names=pls['pools_names'],
            members=pls['pools_members']['members'])

    @util.transation
    def create_member(self, pools):

        pls = util.trata_param_pool(pools)

        plm = poolmember.PoolMember(self._lb)
        return plm.create(
            names=pls['pools_names'],
            members=pls['pools_members']['members'])

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
    @util.connection
    def create_pool(self, pools):
        self.__create_pool(pools)

    def __create_pool(self, pools):

        monitor_associations = []
        pls = util.trata_param_pool(pools)

        mon = monitor.Monitor(self._lb)

        monitor_associations = mon.create_template(
            names=pls['pools_names'],
            healthcheck=pls['pools_healthcheck']
        )

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

            plm.set_states(
                names=pls['pools_names'],
                members=pls['pools_members']['members'],
                monitor_state=pls['pools_members']['monitor'],
                session_state=pls['pools_members']['session'])

        except Exception, e:
            self._lb._channel.System.Session.rollback_transaction()
            if monitor_associations != []:
                template_names = [m['monitor_rule']['monitor_templates'] for m in monitor_associations]
                mon.delete_template(
                    template_names=template_names
                )
            raise base_exceptions.CommandErrorException(e)
        else:
            self._lb._channel.System.Session.submit_transaction()

    @util.connection
    def update_pool(self, pools):
        self.__update_pool(pools)

    def __update_pool(self, pools):
        log.info('update_pool')
        monitor_associations = []
        pls = util.trata_param_pool(pools)

        pl = pool.Pool(self._lb)
        mon = monitor.Monitor(self._lb)

        # get template currents
        monitor_associations_old = pl.get_monitor_association(names=pls['pools_names'])

        # creates templates
        monitor_associations = mon.create_template(
            names=pls['pools_names'],
            healthcheck=pls['pools_healthcheck']
        )

        try:
            self._lb._channel.System.Session.start_transaction()

            pl.remove_monitor_association(names=pls['pools_names'])

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

            plm.set_states(
                names=pls['pools_names'],
                members=pls['pools_members']['members'],
                monitor_state=pls['pools_members']['monitor'],
                session_state=pls['pools_members']['session'])

        except Exception, e:
            self._lb._channel.System.Session.rollback_transaction()

            # delete templates created
            template_names = [m for m in list(itertools.chain(*[m['monitor_rule']['monitor_templates'] for m in monitor_associations])) if 'MONITOR' in m]
            if template_names:
                mon.delete_template(
                    template_names=template_names
                )
            raise base_exceptions.CommandErrorException(e)
        else:
            self._lb._channel.System.Session.submit_transaction()

            # delete templates old
            template_names = [m for m in list(itertools.chain(*[m['monitor_rule']['monitor_templates'] for m in monitor_associations_old])) if 'MONITOR' in m]
            if template_names:
                mon.delete_template(
                    template_names=template_names
                )

    @util.connection
    def delete_pool(self, pools):
        self.delete_pool(pools)

    def __delete_pool(self, pools):
        log.info('delete_pool')

        pls = util.trata_param_pool(pools)

        pl = pool.Pool(self._lb)
        mon = monitor.Monitor(self._lb)
        self._lb._channel.System.Session.start_transaction()
        try:
            monitor_associations = pl.get_monitor_association(names=pls['pools_names'])
            pl.remove_monitor_association(names=pls['pools_names'])
        except Exception, e:
            self._lb._channel.System.Session.rollback_transaction()
            raise base_exceptions.CommandErrorException(e)
        else:
            self._lb._channel.System.Session.submit_transaction()
            try:
                template_names = [m for m in list(itertools.chain(*[m['monitor_rule']['monitor_templates'] for m in monitor_associations])) if 'MONITOR' in m]
                if template_names:
                    mon.delete_template(template_names=template_names)
            except bigsuds.OperationFailed:
                pass
            finally:
                self._lb._channel.System.Session.start_transaction()
                try:
                    pl.delete(names=pls['pools_names'])
                    self._lb._channel.System.Session.submit_transaction()
                except Exception, e:
                    self._lb._channel.System.Session.rollback_transaction()
                    raise base_exceptions.CommandErrorException(e)
