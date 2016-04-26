# -*- coding: utf-8 -*-
import logging

from networkapi.plugins.F5.f5base import F5Base

log = logging.getLogger(__name__)


class ProfileTCP(F5Base):

    def get_list(self):
        profiles = self._lb._channel.LocalLB.ProfileTCP.get_list()
        return profiles

    def create(self, **kwargs):
        log.info('profiletcp:create:%s' % kwargs)
        self._lb._channel.LocalLB.ProfileTCP.create(profile_names=kwargs['profile_names'])

    def set_idle_timeout(self, **kwargs):
        log.info('profiletcp:set_idle_timeout:%s' % kwargs)
        self._lb._channel.LocalLB.ProfileTCP.set_idle_timeout(
            profile_names=kwargs['profile_names'],
            timeouts=kwargs['timeouts']
        )


class ProfileHttp(F5Base):

    def get_list(self):
        profiles = self._lb._channel.LocalLB.ProfileHttp.get_list()
        return profiles

    def create(self, **kwargs):
        log.info('profilehttp:create:%s' % kwargs)
        self._lb._channel.LocalLB.ProfileHttp.create(profile_names=kwargs['profile_names'])


class ProfileFastL4(F5Base):

    def get_list(self):
        profiles = self._lb._channel.LocalLB.ProfileFastL4.get_list()
        return profiles

    def create(self, **kwargs):
        log.info('profilefastl4:create:%s' % kwargs)
        self._lb._channel.LocalLB.ProfileFastL4.create(profile_names=kwargs['profile_names'])

    def set_idle_timeout(self, **kwargs):
        log.info('profilefastl4:set_idle_timeout:%s' % kwargs)
        self._lb._channel.LocalLB.ProfileFastL4.set_idle_timeout(
            profile_names=kwargs['profile_names'],
            timeouts=kwargs['timeouts']
        )


class ProfileUDP(F5Base):

    def get_list(self):
        profiles = self._lb._channel.LocalLB.ProfileUDP.get_list()
        return profiles

    def create(self, **kwargs):
        log.info('profileudp:create:%s' % kwargs)
        self._lb._channel.LocalLB.ProfileUDP.create(profile_names=kwargs['profile_names'])

    def set_idle_timeout(self, **kwargs):
        log.info('profileudp:set_idle_timeout:%s' % kwargs)
        self._lb._channel.LocalLB.ProfileUDP.set_idle_timeout(
            profile_names=kwargs['profile_names'],
            timeouts=kwargs['timeouts']
        )
