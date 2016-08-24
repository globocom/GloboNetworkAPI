# -*- coding:utf-8 -*-
import copy
import logging

from ..base import BasePlugin
from networkapi.plugins.Brocade import util
from networkapi.util import valid_expression
from networkapi.util import valid_regex

log = logging.getLogger(__name__)


class Generic(BasePlugin):

    baddi = None

    #######################################
    # MEMBER
    #######################################
    def _action_member(self, pool, mb, action):

        if pool.get('healthcheck'):
            if action == 'create' or pool['healthcheck'].get('new'):
                healthcheck = pool['healthcheck']
                hr = self._prepare_healthcheck(healthcheck['healthcheck_request'])
                mb['healthcheck'] = {
                    'type': healthcheck['healthcheck_type'],
                    'url_health': hr
                }

        # vip assoc with pool
        for vip in pool['vips']:
            vpc = copy.deepcopy(vip)
            ports = vpc.get('ports')

            address = vpc['ipv4']['ip_formated'] if vpc['ipv4'] else vpc['ipv6']['ip_formated']
            vp = dict()
            vp['name'] = 'VIP_{}'.format(vpc['id'])
            vp['address'] = address

            for port in ports:

                for pool_vip in port['pools']:
                    lb_method = pool_vip['server_pool']['lb_method']
                    vp['lb_method'] = 'LEAST_CONNECTIONS' if lb_method == 'least-conn' else 'ROUND_ROBIN'
                    # pool
                    if int(pool_vip['server_pool']['id']) == int(pool['id']):
                        vp['protocol_port'] = int(port['port'])
                        if action == 'delete':
                            if vip['created']:
                                self.baddi.unbind_member_from_vip(mb, vp)
                            self.baddi.delete_member(mb)
                        if action == 'create':
                            self.baddi.create_member(mb)
                            if vip['created']:
                                self.baddi.bind_member_to_vip(mb, vp)
                        if action == 'update':
                            if vip['created']:
                                self.baddi.set_predictor_on_virtual_server(vp)
                            self.baddi.update_member(mb)

    @util.connection
    def set_state_member(self, pools):
        for pool in pools['pools']:
            for member in pool['pools_members']:
                mb = self.prepare_member(member)
                self.baddi.update_member_status(mb)

    @util.connection
    def get_state_member(self, pools):

        status_pools = list()
        for pool in pools['pools']:
            status = list()
            for member in pool['pools_members']:

                mb = self.prepare_member(member)
                state = self.baddi.get_real_port_status(mb)
                # default 1
                if state == 'DISABLED':
                    healthcheck = '0'
                    user_up_down = '0'
                elif state == 'ENABLED':
                    healthcheck = '0'
                    user_up_down = '1'
                elif state == 'ACTIVE':
                    healthcheck = '1'
                    user_up_down = '1'
                elif state == 'FAILED' or state == 'NOTBOUND':
                    healthcheck = '0'
                    user_up_down = '1'
                else:
                    healthcheck = '0'
                    user_up_down = '0'
                session = user_up_down
                log.info("member: {} - state: {}".format(mb, state))
                status.append(int(healthcheck + session + user_up_down, 2))

            status_pools.append(status)

        return status_pools

    #######################################
    # POOL
    #######################################
    @util.connection
    def create_pool(self, pools):

        for pool in pools['pools']:

            for member in pool['pools_members']:
                mb = self.prepare_member(member)
                self._action_member(pool, mb, 'create')

    @util.connection
    def delete_pool(self, pools):

        for pool in pools['pools']:

            for member in pool['pools_members']:
                mb = self.prepare_member(member)
                self._action_member(pool, mb, 'delete')

    @util.connection
    def update_pool(self, pools):

        for pool in pools['pools']:

            for member in pool['pools_members']:
                mb = self.prepare_member(member)

                if mb.get('new'):
                    self._action_member(pool, mb, 'create')

                elif not mb.get('remove'):
                    self._action_member(pool, mb, 'update')

                elif mb.get('remove'):
                    self._action_member(pool, mb, 'delete')

    #######################################
    # VIP
    #######################################
    @util.connection
    def create_vip(self, vips):
        pools_ins = list()
        for vip in vips['vips']:
            vps = self.prepare_vips(vip)

            for idx, vp in enumerate(vps):
                if idx == 0:
                    pools_ins += self._create_vip(vp, port_default=True)
                else:
                    pools_ins += self._create_vip(vp)

        return pools_ins

    def _create_vip(self, vp, port_default=False):
        pools_ins = list()
        if port_default:
            # creates vip and port default
            try:
                self.baddi.create_vip(vp)
            except:
                pass
            else:
                self.baddi.set_predictor_on_virtual_server(vp)
        else:
            # creates reals ports
            self.baddi.create_virtual_server_port(vp)
            pools_ins = self._create_vip_members(vp)

        return pools_ins

    def _create_vip_members(self, vp):
        pools_ins = list()

        for member in vp.get('members'):
            self.baddi.create_member(member)
            self.baddi.bind_member_to_vip(member, vp)
            pools_ins.append(member.get('pool_id'))

        return pools_ins

    @util.connection
    def update_vip(self, vips):

        pools_del = list()
        pools_ins = list()
        for vip in vips['vips']:
            vps = self.prepare_vips(vip)

            for idx, vp in enumerate(vps):
                if idx != 0:
                    if vp.get('new'):
                        vp['members'] = copy.deepcopy(vp.get('members_new'))
                        pools_ins += self._create_vip(vp)
                    elif vp.get('delete'):
                        pools_del += self._delete_vip(vp)
                    else:
                        vpu = copy.deepcopy(vp)
                        self.baddi.update_vip(vpu)

                        # new pool
                        vpn = copy.deepcopy(vp)
                        vpn['members'] = copy.deepcopy(vpn.get('members_new'))
                        pools_ins += self._create_vip_members(vpn)

                        # pool to delete
                        vpd = copy.deepcopy(vp)
                        vpd['members'] = copy.deepcopy(vpd.get('members_delete'))
                        pools_del = self._delete_vip_members(vpd)

        pools_ins = list(set(pools_ins))
        pools_del = list(set(pools_del))

        return pools_ins, pools_del

    @util.connection
    def delete_vip(self, vips):

        pools_del = list()
        for vip in vips['vips']:
            vps = self.prepare_vips(vip)

            for idx, vp in enumerate(vps):
                if idx != 0:
                    pools_del += self._delete_vip(vp)

        return pools_del

    def _delete_vip(self, vp):

        pools_del = self._delete_vip_members(vp)

        self.baddi.delete_vip(vp)

        return pools_del

    def _delete_vip_members(self, vp):

        pools_del = list()
        for member in vp.get('members'):
            self.baddi.unbind_member_from_vip(member, vp)
            ret = self.baddi.delete_member(member)

            # workaround to return pools deleted
            if ret:
                pools_del.append(member.get('pool_id'))

        return pools_del

    def trata_extends(self, vip_request):
        values = {
            'persistence': None
        }
        if vip_request.get('conf'):
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
        if mbc.get('member_status') is not None:
            member_status = util.get_status_name(
                str(mbc['member_status']))
            mb['admin_state_up'] = member_status['monitor']
        if mbc.get('identifier'):
            mb['name'] = mbc.get('identifier')
        mb['is_remote'] = True
        if mbc.get('limit'):
            mb['max_connections'] = int(mbc['limit'])
        mb['weight'] = int(mbc.get('weight', '0')) or 1

        mb['new'] = mbc.get('new')
        mb['remove'] = mbc.get('remove')

        return mb

    def prepare_vips(self, vip):

        vps = list()
        vp = dict()
        vpc = copy.deepcopy(vip.get('vip_request'))

        ports = vpc.get('ports')
        address = vpc['ipv4']['ip_formated'] if vpc['ipv4'] else vpc['ipv6']['ip_formated']
        values = self.trata_extends(vpc)

        vp['name'] = 'VIP_{}'.format(vpc['id'])
        vp['address'] = address
        vp['description'] = vpc['name']
        vp['timeout'] = vpc['options']['timeout']['nome_opcao_txt']
        vp['session_persistence'] = values['persistence']
        vp['l4_protocol'] = [port['options']['l4_protocol']['nome_opcao_txt'].upper()
                             for port in ports][0]
        vp['tos'] = vpc['options']['dscp']

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
            vppc['members_new'] = list()
            vppc['members_delete'] = list()
            vppc['pools'] = list()
            vppc['new'] = True if not port.get('id') else False
            vppc['delete'] = True if port.get('delete') else False
            for pool in port['pools']:
                vppc['pools'].append(pool['server_pool']['id'])
                for member in pool['server_pool']['pools_members']:
                    mb = self.prepare_member(member)

                    if pool['server_pool'].get('healthcheck'):
                        healthcheck = pool['server_pool']['healthcheck']
                        hr = self._prepare_healthcheck(healthcheck['healthcheck_request'])
                        mb['healthcheck'] = {
                            'type': healthcheck['healthcheck_type'],
                            'url_health': hr
                        }
                        mb['pool_id'] = pool['server_pool']['id']

                    # used in pools new and deleted in ports
                    if not pool.get('id'):
                        vppc['members_new'].append(mb)
                    elif pool.get('delete'):
                        vppc['members_delete'].append(mb)
                    else:
                        vppc['members'].append(mb)

            vps.append(vppc)

        return vps

    def _prepare_healthcheck(self, hr):

        if not hr:
            hr = 'HEAD /'

        rg = '^([\" ]?)+(GET|HEAD|POST|PUT|CONNECT|DELETE|OPTIONS|TRACE|PATCH)'
        if not valid_regex(hr, rg):
            hr = 'GET ' + hr

        # do escape when healthcheck has simple \r\n
        rg = '((\\r\\n))'
        if valid_regex(hr, rg):
            log.debug('adding unicode-escape')
            hr = hr.encode('unicode-escape')

        # add HTTP/1.\\r\\n\\r\\n when plugin no receive in
        # healthcheck
        rg = 'HTTP\/1'
        if not valid_regex(hr, rg):
            log.debug('adding HTTP/1.\\r\\n\\r\\n')
            hr = hr + ' HTTP/1.0\\r\\n\\r\\n'

        # add \\r\\n\\r\\n when plugin no receive in
        # healthcheck
        rg = '(?:((\\r\\n)|(\\\\r\\\\n)){1,2}?)$'
        if not valid_regex(hr, rg):
            log.debug('adding \\r\\n\\r\\n')
            hr = hr + '\\r\\n\\r\\n'

        return hr
