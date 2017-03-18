# -*- coding: utf-8 -*-
# vim: tabstop=4 shiftwidth=4 softtabstop=4
#
# Copyright 2014 Brocade Communication Systems, Inc.  All rights reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
#
#
import functools
import logging
import time

import adx_exception
import suds as suds

LOG = logging.getLogger(__name__)


def log(method):
    @functools.wraps(method)
    def wrapper(*args, **kwargs):
        instance = args[0]
        data = {'class_name': '%s.%s' % (instance.__class__.__module__,
                                         instance.__class__.__name__),
                'method_name': method.__name__,
                'args': args[1:], 'kwargs': kwargs}
        LOG.debug('%(class_name)s method %(method_name)s'
                  ' called with arguments %(args)s %(kwargs)s', data)
        return method(*args, **kwargs)
    return wrapper


ADX_STANDARD_PORTS = [21, 22, 23, 25, 53, 69, 80, 109, 110, 119, 123, 143, 161,
                      389, 443, 554, 636, 993, 995, 1645, 1755, 1812,
                      3389, 5060, 5061, 7070]

ADX_PREDICTOR_MAP = {
    'ROUND_ROBIN': 'ROUND_ROBIN',
    'LEAST_CONNECTIONS': 'LEAST_CONN'
}

ADX_PROTOCOL_MAP = {
    'TCP': 'TCP',
    'HTTP': 'HTTP',
    'HTTPS': 'SSL'
}


class BrocadeAdxDeviceDriverImpl():

    def __init__(self, service_clients):
        self.slb_factory = service_clients[0].factory
        self.slb_service = service_clients[0].service

        self.sys_factory = service_clients[1].factory
        self.sys_service = service_clients[1].service

        self.net_factory = service_clients[2].factory
        self.net_service = service_clients[2].service

    def _adx_server(self, address, name=None):
        server = self.slb_factory.create('Server')
        server.IP = address
        if name:
            server.Name = name
        return server

    def _adx_server_port(self, address, protocol_port, name=None):
        # Create Server
        server = self._adx_server(address, name)

        # Create L4Port
        l4_port = self.slb_factory.create('L4Port')
        l4_port.NameOrNumber = protocol_port

        # Create ServerPort
        server_port = self.slb_factory.create('ServerPort')
        server_port.srvr = server
        server_port.port = l4_port
        return server_port

    def _update_real_server_port_properties(self, new_member):
        try:
            address = new_member['address']
            protocol_port = new_member['protocol_port']
            new_admin_state_up = new_member.get('admin_state_up')
            max_connections = new_member['max_connections']
            healthcheck = new_member.get('healthcheck')

            rs_server_port = self._adx_server_port(address, protocol_port)
            reply = (self.slb_service
                     .getRealServerPortConfiguration(rs_server_port))
            rs_port_conf_seq = (self.slb_factory.create
                                ('ArrayOfRealServerPortConfigurationSequence'))
            reply.rsPortConfig.serverPort = rs_server_port
            reply.rsPortConfig.maxConnection = max_connections
            reply.rsPortConfig.adminState = new_admin_state_up

            if healthcheck:
                port_policy = self._create_update_port_policy(healthcheck)

                if port_policy.get('sslPolInfo'):
                    reply.rsPortConfig.sslPolInfo = port_policy.get(
                        'sslPolInfo')
                else:
                    reply.rsPortConfig.sslPolInfo = None

                if port_policy.get('l4Check'):
                    reply.rsPortConfig.enableL4CheckOnly = port_policy.get(
                        'l4Check')

                if port_policy.get('httpPolInfo'):
                    reply.rsPortConfig.httpPolInfo = port_policy.get(
                        'httpPolInfo')
                else:
                    reply.rsPortConfig.httpPolInfo = None

            rs_port_conf_list = [reply.rsPortConfig]
            rs_port_conf_seq.RealServerPortConfigurationSequence = rs_port_conf_list

            (self.slb_service
             .setRealServersPortConfiguration(rs_port_conf_seq))
        except suds.WebFault as e:
            raise adx_exception.ConfigError(msg=e.message)

    def _update_real_server_port_status(self, new_member):
        try:
            address = new_member['address']
            protocol_port = new_member['protocol_port']
            new_admin_state_up = new_member.get('admin_state_up')

            rs_server_port = self._adx_server_port(address, protocol_port)
            reply = (self.slb_service
                     .getRealServerPortConfiguration(rs_server_port))
            rs_port_conf_seq = (self.slb_factory.create
                                ('ArrayOfRealServerPortConfigurationSequence'))
            reply.rsPortConfig.serverPort = rs_server_port
            reply.rsPortConfig.adminState = new_admin_state_up

            rs_port_conf_list = [reply.rsPortConfig]
            rs_port_conf_seq.RealServerPortConfigurationSequence = rs_port_conf_list

            (self.slb_service
             .setRealServersPortConfiguration(rs_port_conf_seq))
        except suds.WebFault as e:
            raise adx_exception.ConfigError(msg=e.message)

    def _update_real_server_properties(self, new_member):
        try:
            address = new_member['address']
            new_weight = new_member.get('weight')

            rs_server = self._adx_server(address)
            reply = (self.slb_service
                     .getRealServerConfiguration(rs_server))

            rs_conf_seq = (self.slb_factory.create
                           ('ArrayOfRealServerConfigurationSequence'))

            reply.rsConfig.leastConnectionWeight = new_weight

            # Work Around to fix bug in WSDL
            reply.rsConfig.byteRateThresold = None

            rs_conf_list = list()
            rs_conf_list.append(reply.rsConfig)
            rs_conf_seq.RealServerConfigurationSequence = rs_conf_list

            (self.slb_service
             .setRealServersConfiguration(rs_conf_seq))
        except suds.WebFault as e:
            raise adx_exception.ConfigError(msg=e.message)

    def _get_server_port_count(self, ip_address, is_virtual):
        server = self._adx_server(ip_address)
        start_index = 1
        num_retrieved = 5
        api_call = (self.slb_service
                    .getAllVirtualServerPortsSummary if is_virtual
                    else self.slb_service.getAllRealServerPortsSummary)
        try:
            reply = api_call(server, start_index, num_retrieved)
            return reply.genericInfo.totalEntriesAvailable
        except suds.WebFault:
            return 0

    def _is_server_port(self, server_port):
        start_index = 1
        num_retrieved = 5
        api_call = (self.slb_service.getRealServerPortConfiguration)
        try:
            reply = api_call(server_port, start_index, num_retrieved)
            if reply:
                return True
            else:
                return False
        except suds.WebFault:
            return 0

    def _get_server_port_by_virtual_count(self, server_port):
        start_index = 1
        num_retrieved = 5
        api_call = (
            self.slb_service.getAllVirtualServerPortsBoundtoRealServerPort)
        try:
            reply = api_call(server_port, start_index, num_retrieved)
            return reply.genericInfo.totalEntriesAvailable
        except suds.WebFault:
            return 0

    def bind_member_to_vip(self, member, vip):
        rs_ip_address = member['address']
        rs_port = member['protocol_port']
        rs_name = member.get('name', rs_ip_address)

        vs_ip_address = vip['address']
        vs_port = vip['protocol_port']
        vs_name = vip['name']

        try:
            vs_server_port = self._adx_server_port(
                vs_ip_address, vs_port, vs_name)
            rs_server_port = self._adx_server_port(
                rs_ip_address, rs_port, rs_name)

            (self.slb_service
             .bindRealServerPortToVipPort(vs_server_port, rs_server_port))
        except suds.WebFault as e:
            raise adx_exception.ConfigError(msg=e.message)

    def unbind_member_from_vip(self, member, vip):

        rs_ip_address = member['address']
        rs_name = rs_ip_address
        rs_name = member.get('name', rs_ip_address)
        rs_port = member['protocol_port']

        vs_ip_address = vip['address']
        vs_port = vip['protocol_port']
        vs_name = vip['name']

        try:
            vs_server_port = self._adx_server_port(
                vs_ip_address, vs_port, vs_name)
            rs_server_port = self._adx_server_port(
                rs_ip_address, rs_port, rs_name)

            (self.slb_service
             .unbindRealServerPortFromVipPort(vs_server_port, rs_server_port))
            # Need to check alternate solutions rather than sleep
            # Is 5 seconds good enough ?
            time.sleep(5)
        except suds.WebFault as e:
            raise adx_exception.ConfigError(msg=e.message)

    def bind_monitor_to_member(self, healthmonitor, member):
        healthmonitor_name = healthmonitor['id']
        rs_ip_address = member['address']
        rs_port = member['protocol_port']
        rs_name = member.get('name', rs_ip_address)
        rs_admin_state = member.get('admin_state_up', 'DISABLED')
        rs_run_time_status = 'UNDEFINED'

        try:
            rs_server_port = self._adx_server_port(
                rs_ip_address, rs_port, rs_name)

            real_server_port_config = (self.slb_factory
                                       .create('RealServerPortConfiguration'))
            real_server_port_config.serverPort = rs_server_port
            real_server_port_config.adminState = rs_admin_state
            real_server_port_config.runTimeStatus = rs_run_time_status
            real_server_port_config.portPolicyName = healthmonitor_name
            real_server_port_config.enablePeriodicHealthCheck = True

            rs_port_seq = (self.slb_factory
                           .create('ArrayOfRealServerPortConfigurationSequence'))
            (rs_port_seq.RealServerPortConfigurationSequence
             .append(real_server_port_config))
            self.slb_service.setRealServersPortConfiguration(rs_port_seq)
        except suds.WebFault as e:
            raise adx_exception.ConfigError(msg=e.message)

    @log
    def unbind_monitor_from_member(self, healthmonitor, member):

        rs_ip_address = member['address']
        rs_port = member['protocol_port']
        rs_name = member.get('name', rs_ip_address)
        rs_admin_state = member.get('admin_state_up', 'DISABLED')
        rs_run_time_status = 'UNDEFINED'

        try:
            rs_server_port = self._adx_server_port(
                rs_ip_address, rs_port, rs_name)

            real_server_port_config = (self.slb_factory
                                       .create('RealServerPortConfiguration'))
            real_server_port_config.serverPort = rs_server_port
            real_server_port_config.adminState = rs_admin_state
            real_server_port_config.runTimeStatus = rs_run_time_status
            real_server_port_config.portPolicyName = ''
            real_server_port_config.enablePeriodicHealthCheck = False

            rs_port_seq = (self.slb_factory
                           .create('ArrayOfRealServerPortConfigurationSequence'))
            (rs_port_seq.RealServerPortConfigurationSequence
             .append(real_server_port_config))
            self.slb_service.setRealServersPortConfiguration(rs_port_seq)
        except suds.WebFault:
            # raise adx_exception.ConfigError(msg=e.message)
            # ignore the exception until the bug on the XMl API is fixed
            pass

    @log
    def set_predictor_on_virtual_server(self, vip):
        try:
            server = self._adx_server(vip['address'], vip['name'])
            lb_method = vip['lb_method']

            predictor_method_configuration = (self.slb_factory.create
                                              ('PredictorMethodConfiguration'))
            predictor = ADX_PREDICTOR_MAP.get(lb_method)
            if predictor:
                predictor_method_configuration.predictor = predictor
            else:
                error_message = ('Load Balancing Method/Predictor %s '
                                 'not supported') % (lb_method)
                LOG.error(error_message)
                raise adx_exception.UnsupportedFeature(msg=error_message)

            (self.slb_service
             .setPredictorOnVirtualServer(server,
                                          predictor_method_configuration))
        except suds.WebFault as e:
            raise adx_exception.ConfigError(msg=e.message)

    @log
    def _update_virtual_server_properties(self, new_vip, old_vip):
        try:
            address = new_vip['address']
            new_description = new_vip.get('description')
            old_description = old_vip.get('description')

            if new_description == old_description:
                return

            vs_server = self._adx_server(address)
            reply = (self.slb_service
                     .getVirtualServerConfiguration(vs_server))

            vs_conf_seq = (self.slb_factory.create
                           ('ArrayOfVirtualServerConfigurationSequence'))
            if new_description:
                reply.vipConfig.description = new_description

            # Workaround for the XML API Issues
            if reply.vipConfig.stickyAge == 0:
                reply.vipConfig.stickyAge = None
            if reply.vipConfig.tcpAge == 0:
                reply.vipConfig.tcpAge = None
            if reply.vipConfig.udpAge == 0:
                reply.vipConfig.udpAge = None

            vs_conf_list = []
            vs_conf_list.append(reply.vipConfig)
            vs_conf_seq.VirtualServerConfigurationSequence = vs_conf_list

            (self.slb_service
             .setVirtualServersConfiguration(vs_conf_seq))
        except suds.WebFault as e:
            raise adx_exception.ConfigError(msg=e.message)

    def create_virtual_server(self, vip):
        vs_name = vip['name']
        vs_ip_address = vip['address']
        vs_port = vip['protocol_port']
        description = vip['description']
        tos = vip.get('tos')
        l4_protocol = vip.get('l4_protocol')
        timeout = vip.get('timeout')

        server_port = self._adx_server_port(vs_ip_address, vs_port, vs_name)

        try:
            vs_seq = (self.slb_factory
                      .create('ArrayOfVirtualServerConfigurationSequence'))
            vs_config = (self.slb_factory
                         .create('VirtualServerConfiguration'))

            vs_config.virtualServer = server_port.srvr
            vs_config.adminState = True
            vs_config.allowAdvertiseVipRoute = True
            vs_config.enableAdvertiseVipRoute = True
            vs_config.description = description
            if tos:
                vs_config.tosMarking = tos
                vs_config.enableHealthCheckLayer3DSR = True

            if l4_protocol == 'TCP':
                vs_config.tcpAge = timeout
            else:
                vs_config.udpAge = timeout

            # Work Around to define a value for Enumeration Type
            vs_config.predictor = 'ROUND_ROBIN'
            vs_config.trackingMode = 'NONE'
            vs_config.haMode = 'NOT_CONFIGURED'

            (vs_seq.VirtualServerConfigurationSequence
             .append(vs_config))
            (self.slb_service.
             createVirtualServerWithConfiguration(vs_seq))
        except suds.WebFault as e:
            LOG.error('Exception in create_virtual_server '
                      'in device driver : %s', e.message)
            raise adx_exception.ConfigError(msg=e.message)

    @log
    def create_virtual_server_port(self, vip):
        vs_name = vip['name']
        vs_ip_address = vip['address']
        vs_port = vip['protocol_port']
        admin_state_up = vip.get('admin_state_up', 'DISABLED')
        l4_protocol = vip.get('l4_protocol')

        try:
            server_port = self._adx_server_port(
                vs_ip_address, vs_port, vs_name)
            vs_port_seq = (self.slb_factory.create
                           ('ArrayOfVirtualServerPortConfigurationSequence'))
            vs_port_config = (self.slb_factory
                              .create('VirtualServerPortConfiguration'))

            vs_port_config.virtualServer = server_port.srvr
            vs_port_config.port = server_port.port
            vs_port_config.adminState = admin_state_up

            if l4_protocol == 'TCP':
                vs_port_config.tcpOnly = True
            else:
                vs_port_config.udpOnly = True

            session_persistence = vip.get('session_persistence')
            if session_persistence:
                sp_type = session_persistence['type']
                if sp_type == 'SOURCE_IP':
                    vs_port_config.enableSticky = True
                else:
                    error_message = ('Session Persistence of type %s '
                                     'not supported') % (sp_type)
                    LOG.error(error_message)
                    raise adx_exception.UnsupportedFeature(msg=error_message)

            (vs_port_seq.VirtualServerPortConfigurationSequence
             .append(vs_port_config))
            (self.slb_service
             .createVirtualServerPortWithConfiguration(vs_port_seq))
        except suds.WebFault as e:
            raise adx_exception.ConfigError(msg=e.message)

    @log
    def create_vip(self, vip):
        self.create_virtual_server(vip)
        self.create_virtual_server_port(vip)

    @log
    def delete_vip(self, vip):
        address = vip['address']
        port = vip['protocol_port']

        vs_server_port = self._adx_server_port(address, port)
        vip_port_count = self._get_server_port_count(address, True)

        try:
            self.slb_service.deleteVirtualServerPort(vs_server_port)
        except suds.WebFault:
            pass

        try:
            if vip_port_count <= 2:
                self.slb_service.deleteVirtualServer(vs_server_port.srvr)
        except suds.WebFault as e:
            raise adx_exception.ConfigError(msg=e.message)

    @log
    def update_vip(self, new_vip):
        vs_ipaddress = new_vip['address']
        vs_port = new_vip['protocol_port']
        vs_name = new_vip['name']
        vs_server_port = self._adx_server_port(vs_ipaddress, vs_port, vs_name)

        new_session_persistence = new_vip.get('session_persistence')

        LOG.debug('Update Session Persistence')
        if new_session_persistence is None:
            try:
                (self.slb_service
                 .disableStickyOnVirtualServerPort(vs_server_port))
            except suds.WebFault as e:
                raise adx_exception.ConfigError(msg=e.message)
        else:
            type = new_vip['session_persistence']['type']
            if type == 'SOURCE_IP':
                try:
                    (self.slb_service
                     .enableStickyOnVirtualServerPort(vs_server_port))
                except suds.WebFault as e:
                    raise adx_exception.ConfigError(msg=e.message)
            else:
                error_message = ('Session Persistence of type %s '
                                 'not supported') % (type)
                LOG.error(error_message)
                raise adx_exception.UnsupportedFeature(msg=error_message)

    @log
    def _is_port_policy_in_use(self, healthmonitor_name):
        start_index = 1
        num_retrieved = 15
        port_policy_summary_filter = (self.slb_factory
                                      .create('PortPolicySummaryFilter'))
        simple_filter = (self.slb_factory
                         .create('PortPolicySummarySimpleFilter'))
        simple_filter.field = 'POLICY_NAME'
        simple_filter.operator = 'EQUAL_TO'
        simple_filter.value = healthmonitor_name

        port_policy_summary_filter.simpleFilter = simple_filter

        try:
            reply = (self.slb_service
                     .getAllPortPolicies(start_index,
                                         num_retrieved,
                                         port_policy_summary_filter))
            if reply and reply.policyList:
                policy_list = reply.policyList.PortPoliciesSummarySequence
                return any(policy.inUse for policy in policy_list)
            else:
                # Check if Port Policy is bound to a Real Server Port
                # inUse = reply.policy.inUse
                return False
        except suds.WebFault:
            return False

    def _does_port_policy_exist(self, healthmonitor):
        name = healthmonitor['id']
        try:
            reply = self.slb_service.getPortPolicy(name)
            if reply:
                return True
        except suds.WebFault:
            return False
        return False

    @log
    def _validate_delay(self, monitor_type, delay):
        if monitor_type == 'HTTP':
            if delay < 1 or delay > 120:
                raise adx_exception.UnsupportedOption(value=delay,
                                                      name='delay')
        elif monitor_type == 'HTTPS':
            if delay < 5 or delay > 120:
                raise adx_exception.UnsupportedOption(value=delay,
                                                      name='delay')
        elif monitor_type == 'PING':
            if delay < 1 or delay > 10:
                raise adx_exception.UnsupportedOption(value=delay,
                                                      name='delay')

    @log
    def _validate_max_retries(self, monitor_type, max_retries):
        if monitor_type == 'PING':
            if max_retries < 2 or max_retries > 10:
                raise adx_exception.UnsupportedOption(value=max_retries,
                                                      name='max_retries')
        else:
            if max_retries < 1 or max_retries > 5:
                raise adx_exception.UnsupportedOption(value=max_retries,
                                                      name='max_retries')

    @log
    def _create_update_port_policy(self, healthmonitor):

        monitor_type = healthmonitor['type']
        url_health = healthmonitor['url_health']

        port_policy = dict()

        if monitor_type == 'HTTP':
            port_policy['l4Check'] = False
        elif monitor_type == 'HTTPS':
            port_policy['l4Check'] = False
        elif monitor_type == 'TCP':
            port_policy['l4Check'] = True

        expected_codes = '200'

        start_status_codes = []
        end_status_codes = []
        if 'expected_codes' in healthmonitor:
            expected_codes = healthmonitor['expected_codes']
            # parse the expected codes.
            # Format:"200, 201, 300-400, 400-410"
            for code in map(lambda x: x.strip(' '),
                            expected_codes.split(',')):
                if '-' in code:
                    code_range = map(lambda x: x.strip(' '),
                                     code.split('-'))
                    start_status_codes.append(int(code_range[0]))
                    end_status_codes.append(int(code_range[1]))
                else:
                    start_status_codes.append(int(code))
                    end_status_codes.append(int(code))

        if monitor_type == 'HTTP':
            http_port_policy = (self.slb_factory
                                .create('HttpPortPolicy'))
            url_health_check = (self.slb_factory
                                .create('URLHealthCheck'))
            start_codes = (self.slb_factory
                           .create('ArrayOfunsignedIntSequence'))
            end_codes = (self.slb_factory
                         .create('ArrayOfunsignedIntSequence'))

            start_codes.unsignedIntSequence = start_status_codes
            end_codes.unsignedIntSequence = end_status_codes
            url_health_check.url = url_health
            url_health_check.statusCodeRangeStart = start_codes
            url_health_check.statusCodeRangeEnd = end_codes
            http_port_policy.urlStatusCodeInfo = url_health_check
            http_port_policy.healthCheckType = 'SIMPLE'
            http_port_policy.contentMatch = 'WORKING'

            port_policy['httpPolInfo'] = http_port_policy

        elif monitor_type == 'TCP':
            http_port_policy = (self.slb_factory
                                .create('HttpPortPolicy'))
            url_health_check = (self.slb_factory
                                .create('URLHealthCheck'))
            http_port_policy.urlStatusCodeInfo = url_health_check
            http_port_policy.healthCheckType = 'SIMPLE'

            port_policy['httpPolInfo'] = http_port_policy

        elif monitor_type == 'HTTPS':
            ssl_port_policy = (self.slb_factory
                               .create('HttpPortPolicy'))
            url_health_check = (self.slb_factory
                                .create('URLHealthCheck'))
            start_codes = (self.slb_factory
                           .create('ArrayOfunsignedIntSequence'))
            end_codes = (self.slb_factory
                         .create('ArrayOfunsignedIntSequence'))

            url_health_check.url = url_health
            url_health_check.statusCodeRangeStart = start_codes
            url_health_check.statusCodeRangeEnd = end_codes

            ssl_port_policy.urlStatusCodeInfo = url_health_check
            ssl_port_policy.healthCheckType = 'SIMPLE'
            ssl_port_policy.contentMatch = 'WORKING'

            port_policy['sslPolInfo'] = ssl_port_policy

        return port_policy

    @log
    def set_l2l3l4_health_check(self, new_hm, old_hm=None):
        try:
            delay = new_hm['delay']
            self._validate_delay('PING', delay)
            max_retries = new_hm['max_retries']
            self._validate_max_retries('PING', max_retries)

            l2l3l4_health_check = (self.slb_factory
                                   .create('L2L3L4HealthCheck'))
            l2l3l4_health_check.pingInterval = delay
            l2l3l4_health_check.pingRetries = max_retries
            self.slb_service.setL2L3L4HealthCheck(l2l3l4_health_check)
        except suds.WebFault as e:
            raise adx_exception.ConfigError(msg=e.message)

    @log
    def create_health_monitor(self, healthmonitor):
        name = healthmonitor['id']
        monitor_type = healthmonitor['type']

        # Create Port Policy
        # if the Monitor Type is TCP / HTTP / HTTPS
        if monitor_type in ['HTTP', 'HTTPS', 'TCP']:
            if not self._does_port_policy_exist(healthmonitor):
                self._create_update_port_policy(healthmonitor)
            else:
                LOG.debug('Port Policy %s already exists on the device',
                          name)
        elif monitor_type == 'PING':
            m = 'Health Monitor of type PING not supported'
            LOG.error(m)
            raise adx_exception.UnsupportedFeature(msg=m)

    @log
    def delete_health_monitor(self, healthmonitor):
        name = healthmonitor['id']
        monitor_type = healthmonitor['type']

        if monitor_type in ['HTTP', 'HTTPS', 'TCP']:
            if not self._does_port_policy_exist(healthmonitor):
                LOG.debug('Health Monitor %s does not '
                          'exist on the device', name)
                return

            if not self._is_port_policy_in_use(name):
                try:
                    (self.slb_service
                     .deletePortPolicy(name))
                except suds.WebFault as e:
                    raise adx_exception.ConfigError(msg=e.message)
        elif monitor_type == 'PING':
            m = 'Delete of PING Monitor not supported'
            LOG.error(m)
            raise adx_exception.UnsupportedFeature(msg=m)

    @log
    def update_health_monitor(self, new_hm, old_hm):
        monitor_type = new_hm['type']

        # Create Port Policy
        # if the Monitor Type is TCP / HTTP / HTTPS
        if monitor_type in ['HTTP',
                            'HTTPS',
                            'TCP']:
            self._create_update_port_policy(new_hm, False)
        elif monitor_type == 'PING':
            m = 'Health Monitor of type PING not supported'
            LOG.error(m)
            raise adx_exception.UnsupportedFeature(msg=m)

    def _create_real_server(self, member):
        address = member['address']
        weight = member['weight']
        name = member.get('name', address)
        is_remote = member.get('is_remote', False)

        rsportcount = self._get_server_port_count(member['address'], False)

        if rsportcount == 0:
            try:
                rs = self._adx_server(address, name)
                rsconfigsequence = (self.slb_factory.create
                                    ('ArrayOfRealServerConfigurationSequence'))
                rsconfig = (self.slb_factory
                            .create('RealServerConfiguration'))

                rsconfig.realServer = rs
                rsconfig.isRemoteServer = is_remote
                rsconfig.adminState = 'ENABLED'
                rsconfig.leastConnectionWeight = weight
                rsconfig.hcTrackingMode = 'NONE'

                rsconfigsequence.RealServerConfigurationSequence.append(
                    rsconfig)
                (self.slb_service
                 .createRealServerWithConfiguration(rsconfigsequence))
            except suds.WebFault as e:
                LOG.debug('Error in creating Real Server %s', e)
                pass

    def _create_real_server_port(self, member):

        address = member['address']
        port = member['protocol_port']
        admin_state_up = member['admin_state_up']
        name = member.get('name', address)
        is_backup = member.get('is_backup', False)
        max_connections = member['max_connections']
        healthcheck = member.get('healthcheck')

        try:
            # Create Port Profile if it is not a standard port
            if port not in ADX_STANDARD_PORTS:
                port_profile = dict()
                port_profile['protocol_port'] = port
                self._create_port_profile(port_profile)

            rs_server_port = self._adx_server_port(address, port, name)
            rs_port_seq = (self.slb_factory
                           .create('ArrayOfRealServerPortConfigurationSequence'))
            rs_port_config = (self.slb_factory
                              .create('RealServerPortConfiguration'))

            rs_port_config.serverPort = rs_server_port
            rs_port_config.adminState = admin_state_up
            rs_port_config.maxConnection = max_connections
            rs_port_config.isBackup = is_backup

            if healthcheck:
                port_policy = self._create_update_port_policy(healthcheck)
                if port_policy.get('sslPolInfo'):
                    rs_port_config.sslPolInfo = port_policy.get('sslPolInfo')
                if port_policy.get('l4Check'):
                    rs_port_config.enableL4CheckOnly = port_policy.get(
                        'l4Check')
                if port_policy.get('httpPolInfo'):
                    rs_port_config.httpPolInfo = port_policy.get('httpPolInfo')

            # Work Around to define a value for Enumeration Type
            rs_port_config.runTimeStatus = 'UNDEFINED'

            (rs_port_seq.RealServerPortConfigurationSequence
             .append(rs_port_config))

            self.slb_service.createRealServerPortWithConfiguration(rs_port_seq)
        except suds.WebFault as e:
            raise adx_exception.ConfigError(msg=e.message)

    @log
    def create_member(self, member):

        self._create_real_server(member)
        self._create_real_server_port(member)

    @log
    def delete_member(self, member):

        try:
            pool_del = False
            rsserverport = self._adx_server_port(member['address'],
                                                 member['protocol_port'])

            rsportbyvirtualcount = self._get_server_port_by_virtual_count(
                rsserverport)
            if rsportbyvirtualcount == 0:
                pool_del = True
                rsportbyserver = self._is_server_port(rsserverport)
                if rsportbyserver:
                    self.slb_service.deleteRealServerPort(rsserverport)

            # Delete the Real Server
            # if this is the only port other than default port
            time.sleep(5)
            rsportcount = self._get_server_port_count(member['address'], False)

            # work around to delete real
            if rsportcount <= 1:
                pool_del = True

                self.slb_service.deleteRealServer(rsserverport.srvr)

            return pool_del

        except suds.WebFault as e:
            raise adx_exception.ConfigError(msg=e.message)

    @log
    def update_member(self, new_member):

        self._update_real_server_properties(new_member)
        self._update_real_server_port_properties(new_member)

    @log
    def update_member_status(self, new_member):
        self._update_real_server_port_status(new_member)

    @log
    def write_mem(self):
        try:
            self.sys_service.writeConfig()
        except Exception as e:
            raise adx_exception.ConfigError(msg=e.message)

    @log
    def get_version(self):
        try:
            return self.sys_service.getVersion()
        except Exception:
            return None

    @log
    def create_pool(self, pool):
        pool_name = pool['name']

        try:
            server_group_list = (self.slb_factory.create
                                 ('ArrayOfRealServerGroupSequence'))
            real_server_group = (self.slb_factory
                                 .create('RealServerGroup'))
            real_server_group.groupName = pool_name
            server_group_list.RealServerGroupSequence.append(real_server_group)

            real_servers_list = (self.slb_factory
                                 .create('ArrayOfStringSequence'))

            for member in pool['members']:
                real_servers_list.StringSequence.append(member)

            real_server_group.realServers = real_servers_list

            (self.slb_service
             .createRealServerGroups(server_group_list))
        except suds.WebFault as e:
            raise adx_exception.ConfigError(msg=e.message)

    @log
    def update_pool(self, new_pool, old_pool):
        pass

    @log
    def delete_pool(self, pool):
        pool_name = pool['name']
        try:
            server_group_list = (self.slb_factory
                                 .create('ArrayOfStringSequence'))
            server_group_list.StringSequence.append(pool_name)

            (self.slb_service
             .deleteRealServerGroups(server_group_list))
        except suds.WebFault as e:
            raise adx_exception.ConfigError(msg=e.message)

    @log
    def get_pool_stats(self, pool_id, members):
        bytes_in = 0
        bytes_out = 0
        active_connections = 0
        total_connections = 0

        for m in members:
            try:
                rs_ip_address = m['address']
                rs_name = m['address']
                rs_port = m['protocol_port']
                rs_server_port = self._adx_server_port(rs_ip_address,
                                                       rs_port, rs_name)
                reply = (self.slb_service
                         .getRealServerPortMonitoringDetails(rs_server_port))

                statistics = reply.statistics.statistics
                bytes_in += statistics.rxBytes
                bytes_out += statistics.txBytes
                active_connections += statistics.currentConn
                total_connections += statistics.totalConn

            except suds.WebFault:
                pass

        return {'bytes_in': bytes_in,
                'bytes_out': bytes_out,
                'active_connections': active_connections,
                'total_connections': total_connections}

    @log
    def _create_port_profile(self, port):
        port = port['protocol_port']
        try:
            port_profile = self.slb_factory.create('PortProfile')
            l4_port = self.slb_factory.create('L4Port')
            l4_port.NameOrNumber = port
            port_profile.port = l4_port
            port_profile.portType = 'TCP'
            port_profile.status = True

            self.slb_service.createPortProfile(port_profile)
        except suds.WebFault as e:
            LOG.debug('Exception in create port profile %s', e)

    @log
    def _delete_port_profile(self, port_profile):
        protocol_port = port_profile['protocol_port']
        try:
            l4_port = self.slb_factory.create('L4Port')
            l4_port.NameOrNumber = protocol_port
            self.slb_service.deletePortProfile(l4_port)
        except suds.WebFault as e:
            LOG.debug('Exception in Delete Port Profile %s', e)

    @log
    def ifconfig_e1(self, ip_address, cidr):
        # Configure route only on e1
        try:

            (network, mask) = cidr.split('/')

            ifconfig = self.net_factory.create('InterfaceConfig')
            ifconfig.id.interfaceType = 'ETHERNET'
            ifconfig.id.portString = '1'
            ifconfig.isRouteOnly = True

            interface_config_seq = self.net_factory.create(
                'ArrayOfInterfaceConfigSequence')
            interface_config_seq.InterfaceConfigSequence.append(ifconfig)

            self.net_service.setInterfaceConfig(interface_config_seq)

            # Configure ip address on e1
            ifid = self.net_factory.create('InterfaceID')
            ipaddr_seq = (self.net_factory
                          .create('ArrayOfInterfaceIPAddressSequence'))
            ipaddr = self.net_factory.create('InterfaceIPAddress')

            ifid.portString = '1'
            ifid.interfaceType = 'ETHERNET'
            ipaddr.ip = ip_address
            ipaddr.subnetMaskLength = mask

            ipaddr_seq.InterfaceIPAddressSequence.append(ipaddr)

            # Sending operations to the vLb
            self.net_service.setInterfaceConfig(interface_config_seq)
            self.net_service.addIPsToInterface(ifid, ipaddr_seq)
        except suds.WebFault as e:
            LOG.debug('Exception configuring e1 %s', e)
            raise adx_exception.ConfigError(msg=e.message)

    @log
    def create_static_route(self,
                            dest_ip_address,
                            network_mask,
                            nexthop_ip_address):
        try:
            static_route = self.net_factory.create('StaticRoute')
            static_route_seq = (self.net_factory
                                .create('ArrayOfStaticRouteSequence'))

            static_route.staticRouteType = 'STANDARD'
            static_route.ipVersion = 'IPV4'
            static_route.destIPAddress = dest_ip_address
            static_route.networkMaskBits = network_mask
            static_route.nexthopIPAddress = nexthop_ip_address

            static_route_seq.StaticRouteSequence.append(static_route)

            self.net_service.createStaticRoute(static_route_seq)
        except suds.WebFault as e:
            LOG.debug('Exception configuring static route %s', e)
            raise adx_exception.ConfigError(msg=e.message)

    @log
    def enable_source_nat(self):
        try:
            global_config = self.slb_factory.create('GlobalSlbConfiguration')
            global_config.enableSourceNat = True
            self.slb_service.updateSlbGlobalConfiguration(global_config)
        except suds.WebFault as e:
            LOG.debug(('Exception enabling source nat %s'), e)
            raise adx_exception.ConfigError(msg=e.message)

    @log
    def get_real_port_status(self, member):

        rsserverport = self._adx_server_port(member['address'],
                                             member['protocol_port'])
        api_call = (self.slb_service.getRealServerPortStatus)
        try:
            reply = api_call(rsserverport)
            return reply.rsPortStatus.status
        except suds.WebFault:
            return 0
