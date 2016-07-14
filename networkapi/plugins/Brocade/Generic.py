import copy
import logging

from networkapi.plugins.Brocade import util
from networkapi.plugins.Brocade.adx_device_driver_impl import BrocadeAdxDeviceDriverImpl

from ..base import BasePlugin

log = logging.getLogger(__name__)


class Generic(BasePlugin):

    #######################################
    # POOL
    #######################################
    @util.connection
    def create_pool(self, pools):

        baddi = BrocadeAdxDeviceDriverImpl(service_clients=self._lb.service_clients)
        import pdb; pdb.Pdb(skip=['django.*']).set_trace()  # breakpoint 603d1364 //

        for pool in pools['pools']:
            for member in pool['pools_members']:
                mbc = copy.deepcopy(member)
                mb = dict()

                mb['address'] = mbc['ip']
                mb['protocol_port'] = int(mbc['port'])
                member_status = util.get_status_name(
                    str(mbc['member_status']))
                mb['admin_state_up'] = member_status['monitor']
                mb['name'] = 'teste123'
                mb['is_remote'] = True
                mb['max_connections'] = int(mbc['limit'])
                mb['weight'] = int(mbc['weight']) or 1

                baddi.create_member(mb)

    @util.connection
    def delete_pool(self, pools):

        baddi = BrocadeAdxDeviceDriverImpl(service_clients=self._lb.service_clients)

        for pool in pools['pools']:
            for member in pool['pools_members']:
                mbc = copy.deepcopy(member)
                mb = dict()

                mb['address'] = mbc['ip']
                mb['protocol_port'] = mbc['port']
                baddi.delete_member(mb)

#     @util.connection
#     def create_pool(self, pools):
#         self.__create_pool(pools)

#     def __create_pool(self, data):
#         import pdb; pdb.Pdb(skip=['django.*']).set_trace()  # breakpoint bc0dc317 //

#         log.info("skipping create pool")
#         return

# pool_names = ['P123_teste2','P123_teste3']
# servergrouplist = (_lb.slb_factory.create('ArrayOfRealServerGroupSequence'))
# for pool_name in pool_names:
#     realservergroup = (_lb.slb_factory.create('RealServerGroup'))
#     realservergroup.groupName = pool_name
#     servergrouplist.RealServerGroupSequence.append(realservergroup)

# (_lb.slb_service.createRealServerGroups(servergrouplist))


# servergrouplist = (_lb.slb_factory.create('ArrayOfStringSequence'))
# for pool_name in pool_names:
#     servergrouplist.StringSequence.append(pool_name)

# (_lb.slb_service.deleteRealServerGroups(servergrouplist))

# addRealServersToGroup

# servergrouplist = (_lb.slb_factory.create('ArrayOfRealServerGroupSequence'))
# for pool in pools:
#     realservergroup = (_lb.slb_factory.create('RealServerGroup'))
#     realservergroup.groupName = pool['identifier']
#     realservers = (_lb.slb_factory.create('ArrayOfStringSequence'))
#     for member in pool['server_pool_members']:
#         member_name = member.get('ip').get('ip_formated') if member.get('ip') \
#             else member.get('ipv6').get('ip_formated')
#         realservergroup.realservers.StringSequence.append(member_name)

#     servergrouplist.RealServerGroupSequence.append(realservergroup)

# (_lb.slb_service.createRealServerGroups(servergrouplist))

#         try:
#             for pool in data["pools"]:
#                 pool_name = "P%s_%s" % (pool["id"], pool["nome"])

#                 servergrouplist = (self._lb.slb_factory.create
#                                    ('ArrayOfRealServerGroupSequence'))
#                 realservergroup = (self._lb.slb_factory
#                                    .create('RealServerGroup'))

#                 realservergroup.groupName = pool_name
#                 servergrouplist.RealServerGroupSequence.append(realservergroup)

#                 (self._lb.slb_service
#                  .createRealServerGroups(servergrouplist))
#         except suds.WebFault as e:
#             raise base_exceptions.CommandErrorException(e)

#     @util.connection
#     def update_pool(self, pools):
#         self.__update_pool(pools)

#     def __update_pool(self, pools):
#         log.info('update_pool')
#         monitor_associations = []
#         pls = util.trata_param_pool(pools)

#         pl = pool.Pool(self._lb)
#         mon = monitor.Monitor(self._lb)

#         # get template currents
#         monitor_associations_old = pl.get_monitor_association(names=pls['pools_names'])

#         # creates templates
#         monitor_associations = mon.create_template(
#             names=pls['pools_names'],
#             healthcheck=pls['pools_healthcheck']
#         )

#         try:
#             self._lb._channel.System.Session.start_transaction()

#             pl.remove_monitor_association(names=pls['pools_names'])

#             pl.set_monitor_association(monitor_associations=monitor_associations)

#             pl.set_lb_method(
#                 names=pls['pools_names'],
#                 lbmethod=pls['pools_lbmethod'])

#             pl.set_service_down_action(
#                 names=pls['pools_names'],
#                 actions=pls['pools_actions'])

#             plm = poolmember.PoolMember(self._lb)

#             if pls['pools_members']['members_remove']:
#                 plm.remove(
#                     names=pls['pools_names'],
#                     members=pls['pools_members']['members_remove'])

#             if pls['pools_members']['members_new']:
#                 plm.create(
#                     names=pls['pools_names'],
#                     members=pls['pools_members']['members_new'])

#             plm.set_connection_limit(
#                 names=pls['pools_names'],
#                 members=pls['pools_members']['members'],
#                 connection_limit=pls['pools_members']['limit'])

#             plm.set_priority(
#                 names=pls['pools_names'],
#                 members=pls['pools_members']['members'],
#                 priority=pls['pools_members']['priority'])

#             plm.set_states(
#                 names=pls['pools_names'],
#                 members=pls['pools_members']['members'],
#                 monitor_state=pls['pools_members']['monitor'],
#                 session_state=pls['pools_members']['session'])

#         except Exception, e:
#             self._lb._channel.System.Session.rollback_transaction()

#             # delete templates created
#             template_names = [m for m in list(itertools.chain(*[m['monitor_rule']['monitor_templates'] for m in monitor_associations])) if 'MONITOR' in m]
#             if template_names:
#                 mon.delete_template(
#                     template_names=template_names
#                 )
#             raise base_exceptions.CommandErrorException(e)
#         else:
#             self._lb._channel.System.Session.submit_transaction()

#             # delete templates old
#             template_names = [m for m in list(itertools.chain(*[m['monitor_rule']['monitor_templates'] for m in monitor_associations_old])) if 'MONITOR' in m]
#             if template_names:
#                 mon.delete_template(
#                     template_names=template_names
#                 )

#     @util.connection
#     def delete_pool(self, data):
#         self.__delete_pool(data)

#     def __delete_pool(self, data):

#         for pool in data["pools"]:
#             try:
#                 pool_name = "P%s_%s" % (pool["id"], pool["nome"])
#                 log.info('deleting pool %s' % pool_name)
#                 servergrouplist = (self._lb.slb_factory
#                                    .create('ArrayOfStringSequence'))
#                 servergrouplist.StringSequence.append(pool_name)

#                 (self._lb.slb_service
#                  .deleteRealServerGroups(pool_name))
#             except suds.WebFault as e:
#                 raise base_exceptions.CommandErrorException(e)
