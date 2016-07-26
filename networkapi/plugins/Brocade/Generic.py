import copy
import logging

from networkapi.plugins.Brocade import util
from networkapi.util import valid_expression

from ..base import BasePlugin

log = logging.getLogger(__name__)


class Generic(BasePlugin):

    baddi = None

    #######################################
    # MEMBER
    #######################################
    def _create_member(self, pool):
        members = list()
        for member in pool['pools_members']:
            mb = self.prepare_member(member)
            self.baddi.create_member(mb)
            members.append(mb)
        return members

    def _delete_member(self, pool):
        for member in pool['pools_members']:
            mb = self.prepare_member(member)
            self.baddi.delete_member(mb)

    #######################################
    # POOL
    #######################################
    @util.connection
    def create_pool(self, pools):

        self._create_pool(pools)

    def _create_pool(self, pools):
        for pool in pools['pools']:
            pl = dict()

            members = self._create_member(pool)

            pl['members'] = [mbc['identifier'] for mbc in members]
            pl['name'] = util.trata_nome(pool['nome'])
            self.baddi.create_pool(pl)

    @util.connection
    def delete_pool(self, pools):
        self._delete_pool(pools)

    def _delete_pool(self, pools):
        for pool in pools['pools']:

            pl = dict()
            pl['name'] = util.trata_nome(pool['nome'])
            self.baddi.delete_pool(pl)

    #######################################
    # VIP
    #######################################
    @util.connection
    def create_vip(self, vips):

        for vip in vips['vips']:
            vps = self.prepare_vips(vip)

            for idx, vp in enumerate(vps):
                if idx == 0:
                    # creates vip and port default
                    self.baddi.create_vip(vp)
                    self.baddi.set_predictor_on_virtual_server(vp)
                else:
                    # creates reals ports
                    self.baddi.create_virtual_server_port(vp)

                for member in vp.get('members'):
                    self.baddi.create_member(member)
                    self.baddi.bind_member_to_vip(member, vp)

    @util.connection
    def delete_vip(self, vips):

        pools_del = list()

        for vip in vips['vips']:
            vps = self.prepare_vips(vip)

            for idx, vp in enumerate(vps):
                for member in vp.get('members'):
                    self.baddi.unbind_member_from_vip(member, vp)
                    self.baddi.create_member(member)

                self.baddi.delete_vip(vp)
                pools_del += vp.get('pools')

        return pools_del

    def trata_extends(self, vip_request):
        values = {
            'persistence': None
        }
        conf = vip_request.get('conf').get('conf').get('optionsvip_extended')
        if conf:
            requiments = conf.get('requiments')
            if requiments:
                for requiment in requiments:
                    condicionals = requiment.get('condicionals')
                    for condicional in condicionals:

                        validated = True

                        validations = condicional.get('validations')
                        for validation in validations:
                            if validation.get('type') == 'optionvip':
                                validated &= valid_expression(
                                    validation.get('operator'),
                                    int(vip_request['options'][validation.get('variable')]['id']),
                                    int(validation.get('value'))
                                )

                        if validated:
                            use = condicional.get('use')
                            for item in use:

                                if item.get('type') == 'persistence':
                                    if item.get('value'):
                                        values['persistence'] = {
                                            'type': item.get('value')
                                        }

        return values

    def prepare_member(self, member):
        mbc = copy.deepcopy(member)
        mb = dict()

        mb['address'] = mbc['ip']
        mb['protocol_port'] = int(mbc['port'])
        member_status = util.get_status_name(
            str(mbc['member_status']))
        mb['admin_state_up'] = member_status['monitor']
        mb['name'] = mbc['identifier']
        mb['is_remote'] = True
        mb['max_connections'] = int(mbc['limit'])
        mb['weight'] = int(mbc['weight']) or 1

        return mb

    def prepare_vips(self, vip):
        vps = list()
        vp = dict()
        vpc = copy.deepcopy(vip.get('vip_request'))

        ports = vpc.get('ports')
        address = vpc['ipv4']['ip_formated'] if vpc['ipv4'] else vpc['ipv6']['ip_formated']
        values = self.trata_extends(vpc)

        vp['name'] = 'VIP_{}_{}'.format(vpc['id'], address)
        vp['address'] = address
        vp['description'] = vpc['name']
        vp['timeout'] = vpc['options']['timeout']['nome_opcao_txt']
        vp['session_persistence'] = values['persistence']
        vp['l4_protocol'] = [port['options']['l4_protocol']['nome_opcao_txt'].upper()
                             for port in ports][0]

        lb_method = [pool['server_pool']['lb_method']
                     for pool in port['pools'] for port in ports][0]
        vp['lb_method'] = 'LEAST_CONNECTIONS' if lb_method == 'least-conn' else 'ROUND_ROBIN'

        # prepare member default
        vppc_default = copy.deepcopy(vp)
        vppc_default['protocol_port'] = 'default'
        vppc_default['admin_state_up'] = 'DISABLED'
        vppc_default['session_persistence'] = ''
        vppc_default['members'] = list()
        vppc_default['pools'] = list()
        vps.append(vppc_default)

        # reals members
        for port in ports:
            vppc = copy.deepcopy(vp)
            vppc['protocol_port'] = int(port['port'])
            vppc['admin_state_up'] = 'ENABLED'
            vppc['members'] = list()
            vppc['pools'] = list()
            for pool in port['pools']:
                vppc['pools'].append(pool['id'])
                for member in pool['server_pool']['pools_members']:
                    mb = self.prepare_member(member)
                    vppc['members'].append(mb)
            vps.append(vppc)

        return vps
        # vip_request['options']['dscp']

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
