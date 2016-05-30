import logging

from networkapi.plugins.Brocade.base import Base


log = logging.getLogger(__name__)


class PoolMember(Base):

    def _create_real_server(self, member):
        address = member['address']
        weight = member['weight']
        name = address
        if member.get('name'):
            name = member['name']
        is_remote = member.get('is_remote', False)

        try:
            rs = self._adx_server(address, name)
            rsConfigSequence = (self.slb_factory.create
                                ('ArrayOfRealServerConfigurationSequence'))
            rsConfig = (self.slb_factory
                        .create('RealServerConfiguration'))

            rsConfig.realServer = rs
            rsConfig.isRemoteServer = is_remote
            rsConfig.adminState = 'ENABLED'
            rsConfig.leastConnectionWeight = weight
            rsConfig.hcTrackingMode = 'NONE'

            rsConfigSequence.RealServerConfigurationSequence.append(rsConfig)
            (self.slb_service
             .createRealServerWithConfiguration(rsConfigSequence))
        except suds.WebFault as e:
            LOG.debug(_('Error in creating Real Server %s'), e)
            pass

    def _create_real_server_port(self, member):
        address = member['address']
        port = member['protocol_port']
        admin_state_up = member['admin_state_up']
        name = address
        if member.get('name'):
            name = member['name']
        is_backup = member.get('is_backup', False)

        try:
            # Create Port Profile if it is not a standard port
            if port not in ADX_STANDARD_PORTS:
                port_profile = dict()
                port_profile['protocol_port'] = port
                self._create_port_profile(port_profile)

            rsServerPort = self._adx_server_port(address, port, name)
            rsPortSeq = (self.slb_factory
                         .create('ArrayOfRealServerPortConfigurationSequence'))
            rsPortConfig = (self.slb_factory
                            .create('RealServerPortConfiguration'))

            rsPortConfig.serverPort = rsServerPort
            rsAdminState = 'ENABLED' if admin_state_up else 'DISABLED'
            rsPortConfig.adminState = rsAdminState
            if 'max_connections' in member:
                rsPortConfig.maxConnection = member['max_connections']
            rsPortConfig.isBackup = is_backup

            # Work Around to define a value for Enumeration Type
            rsPortConfig.runTimeStatus = 'UNDEFINED'

            (rsPortSeq.RealServerPortConfigurationSequence
             .append(rsPortConfig))

            self.slb_service.createRealServerPortWithConfiguration(rsPortSeq)
        except suds.WebFault as e:
            raise adx_exception.ConfigError(msg=e.message)

    def set_states(self, **kwargs):
        for k, v in kwargs.items():
            if v == []:
                return

        self._lb._channel.LocalLB.Pool.set_member_session_enabled_state(
            kwargs['names'],
            kwargs['members'],
            kwargs['session_state'])
        self._lb._channel.LocalLB.Pool.set_member_monitor_state(
            kwargs['names'],
            kwargs['members'],
            kwargs['monitor_state'])

    def get_states(self, **kwargs):
        for k, v in kwargs.items():
            if v == []:
                return

        monitors = self._lb._channel.LocalLB.Pool.get_member_monitor_status(
            kwargs['names'],
            kwargs['members'])

        sessions = self._lb._channel.LocalLB.Pool.get_member_session_status(
            kwargs['names'],
            kwargs['members'])

        status_pools = []
        for p, pool in enumerate(monitors):
            status = []
            for s, state in enumerate(pool):
                if state == 'MONITOR_STATUS_UP':
                    healthcheck = '1'
                    monitor = '1'
                elif state == 'MONITOR_STATUS_DOWN':
                    healthcheck = '0'
                    monitor = '1'
                elif state == 'MONITOR_STATUS_FORCED_DOWN':
                    healthcheck = '0'
                    monitor = '0'
                else:
                    healthcheck = '0'
                    monitor = '0'

                if sessions[p][s] == 'SESSION_STATUS_ENABLED':
                    session = '1'
                elif sessions[p][s] == 'SESSION_STATUS_DISABLED':
                    session = '0'
                else:
                    session = '0'

                status.append(int(healthcheck + session + monitor, 2))

            status_pools.append(status)
        return status_pools

    def set_connection_limit(self, **kwargs):
        for k, v in kwargs.items():
            if v == []:
                return

        self._lb._channel.LocalLB.Pool.set_member_connection_limit(
            kwargs['names'],
            kwargs['members'],
            kwargs['connection_limit'])

    def set_priority(self, **kwargs):
        for k, v in kwargs.items():
            if v == []:
                return

        self._lb._channel.LocalLB.Pool.set_member_priority(
            kwargs['names'],
            kwargs['members'],
            kwargs['priority'],)

    def create(self, **kwargs):
        for k, v in kwargs.items():
            if v == []:
                return

        log.info(kwargs)
        names = [kwargs['names'][k] for k, n in enumerate(kwargs['members']) if kwargs['names'][k] and kwargs['members'][k]]
        members = [kwargs['members'][k] for k, n in enumerate(kwargs['members']) if kwargs['names'][k] and kwargs['members'][k]]

        if names:
            self._lb._channel.LocalLB.Pool.add_member_v2(
                pool_names=names,
                members=members)

    def remove(self, **kwargs):
        for k, v in kwargs.items():
            if v == []:
                return

        names = [kwargs['names'][k] for k, n in enumerate(kwargs['members']) if kwargs['names'][k] and kwargs['members'][k]]
        members = [kwargs['members'][k] for k, n in enumerate(kwargs['members']) if kwargs['names'][k] and kwargs['members'][k]]

        if names:
            self._lb._channel.LocalLB.Pool.remove_member_v2(
                pool_names=names,
                members=members)

    def __repr__(self):
        log.info('%s' % (self._lb))
        return self._lb
