import itertools
import logging

from networkapi.plugins import exceptions as base_exceptions
from networkapi.plugins.Brocade import monitor, pool, poolmember, util, virtualserver

import suds

from ..base import BasePlugin

log = logging.getLogger(__name__)


class Generic(BasePlugin):
    ######################################
    # VIP
    ######################################

    @util.connection
    def delete_vip(self, vips):
        tratado = util.trata_param_vip(vips)
        try:
            self._lb._channel.System.Session.start_transaction()
            vts = virtualserver.VirtualServer(self._lb)
            vps_names = [vp['name'] for vp in tratado['vips_filter']]
            vts.delete(vps_names=vps_names)
        except Exception, e:
            raise base_exceptions.CommandErrorException(e)
        else:
            self._lb._channel.System.Session.submit_transaction()

            self.__delete_pool({'pools': tratado['pool_filter_created']})

    @util.connection
    def create_vip(self, vips):
        tratado = util.trata_param_vip(vips)

        if tratado['pool_filter']:
            self.__create_pool({'pools': tratado['pool_filter']})
        try:
            vts = virtualserver.VirtualServer(self._lb)
            vts.create(vips=tratado['vips_filter'])
        except Exception, e:
            raise base_exceptions.CommandErrorException(e)

    #######################################
    # POOLMEMBER
    #######################################
    # TODO:transaction
    @util.connection
    def set_state_member(self, pools):

        pls = util.trata_param_pool(pools)

        plm = poolmember.PoolMember(self._lb)

        plm.set_states(
            names=pls['pools_names'],
            members=pls['pools_members']['members'],
            monitor_state=pls['pools_members']['monitor'],
            session_state=pls['pools_members']['session'])

    # TODO:transaction
    @util.connection
    def set_connection_limit_member(self, pools):

        pls = util.trata_param_pool(pools)

        plm = poolmember.PoolMember(self._lb)
        plm.setConnectionLimit(
            names=pls['pools_names'],
            members=pls['pools_members']['members'],
            connection_limit=pls['pools_members']['limit'])

    # TODO:transaction
    @util.connection
    def set_priority_member(self, pools):

        pls = util.trata_param_pool(pools)

        plm = poolmember.PoolMember(self._lb)
        plm.setPriority(
            names=pls['pools_names'],
            members=pls['pools_members']['members'],
            priority=pls['pools_members']['priority'])

    # TODO:transaction
    @util.connection
    def get_state_member(self, pools):
        pls = util.trata_param_pool(pools)

        plm = poolmember.PoolMember(self._lb)
        return plm.get_states(
            names=pls['pools_names'],
            members=pls['pools_members']['members'])

    # TODO:transaction
    @util.connection
    def create_member(self, pools):

        pls = util.trata_param_pool(pools)

        plm = poolmember.PoolMember(self._lb)
        return plm.create(
            names=pls['pools_names'],
            members=pls['pools_members']['members'])

    # TODO:transaction
    @util.connection
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

    def __create_pool(self, data):
        log.info("skipping create pool")
        # return

        try:
            for pool in data["pools"]:
                pool_name = "P%s_%s" % (pool["id"], pool["nome"])

                servergrouplist = (self._lb.slb_factory.create
                                   ('ArrayOfRealServerGroupSequence'))
                realservergroup = (self._lb.slb_factory
                                   .create('RealServerGroup'))

                realservergroup.groupName = pool_name
                servergrouplist.RealServerGroupSequence.append(realservergroup)

                (self._lb.slb_service
                 .createRealServerGroups(servergrouplist))
        except suds.WebFault as e:
            raise base_exceptions.CommandErrorException(e)

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
    def delete_pool(self, data):
        self.__delete_pool(data)

    def __delete_pool(self, data):

        for pool in data["pools"]:
            try:
                pool_name = "P%s_%s" % (pool["id"], pool["nome"])
                log.info('deleting pool %s' % pool_name)
                servergrouplist = (self._lb.slb_factory
                                   .create('ArrayOfStringSequence'))
                servergrouplist.StringSequence.append(pool_name)

                (self._lb.slb_service
                 .deleteRealServerGroups(pool_name))
            except suds.WebFault as e:
                raise base_exceptions.CommandErrorException(e)
