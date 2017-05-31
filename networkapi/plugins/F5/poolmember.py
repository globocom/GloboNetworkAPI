# -*- coding: utf-8 -*-
import logging

from networkapi.plugins.F5.f5base import F5Base
from networkapi.plugins.F5.util import logger

log = logging.getLogger(__name__)


class PoolMember(F5Base):

    @logger
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

    @logger
    def set_member_monitor_state(self, **kwargs):
        for k, v in kwargs.items():
            if v == []:
                return

        self._lb._channel.LocalLB.Pool.set_member_monitor_state(
            kwargs['names'],
            kwargs['members'],
            kwargs['monitor_state'])

    @logger
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

    @logger
    def set_connection_limit(self, **kwargs):
        for k, v in kwargs.items():
            if v == []:
                return

        self._lb._channel.LocalLB.Pool.set_member_connection_limit(
            kwargs['names'],
            kwargs['members'],
            kwargs['connection_limit'])

    @logger
    def set_priority(self, **kwargs):
        for k, v in kwargs.items():
            if v == []:
                return

        self._lb._channel.LocalLB.Pool.set_member_priority(
            kwargs['names'],
            kwargs['members'],
            kwargs['priority'],)

    @logger
    def create(self, **kwargs):
        for k, v in kwargs.items():
            if v == []:
                return

        names = [kwargs['names'][k] for k, n in enumerate(kwargs['members']) if kwargs[
            'names'][k] and kwargs['members'][k]]
        members = [kwargs['members'][k] for k, n in enumerate(
            kwargs['members']) if kwargs['names'][k] and kwargs['members'][k]]

        if names:
            self._lb._channel.LocalLB.Pool.add_member_v2(
                pool_names=names,
                members=members)

    @logger
    def remove(self, **kwargs):
        for k, v in kwargs.items():
            if v == []:
                return

        names = [kwargs['names'][k] for k, n in enumerate(kwargs['members']) if kwargs[
            'names'][k] and kwargs['members'][k]]
        members = [kwargs['members'][k] for k, n in enumerate(
            kwargs['members']) if kwargs['names'][k] and kwargs['members'][k]]

        if names:
            self._lb._channel.LocalLB.Pool.remove_member_v2(
                pool_names=names,
                members=members)

    @logger
    def set_member_description(self, **kwargs):
        for k, v in kwargs.items():
            if v == []:
                return

        self._lb._channel.LocalLB.Pool.set_member_description(
            kwargs['names'],
            kwargs['members'],
            kwargs['description'])

    def __repr__(self):
        log.info('%s' % (self._lb))
        return self._lb
