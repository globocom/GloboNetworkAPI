# -*- coding: utf-8 -*-
import logging

from networkapi.plugins.F5.f5base import F5Base
from networkapi.plugins.F5.util import logger

log = logging.getLogger(__name__)


class ProfileTCP(F5Base):

    @logger
    def get_list(self):
        profiles = self._lb._channel.LocalLB.ProfileTCP.get_list()
        return profiles

    @logger
    def create(self, **kwargs):
        self._lb._channel.LocalLB.ProfileTCP.create(
            profile_names=kwargs['profile_names'])

    @logger
    def set_idle_timeout(self, **kwargs):
        self._lb._channel.LocalLB.ProfileTCP.set_idle_timeout(
            profile_names=kwargs['profile_names'],
            timeouts=kwargs['timeouts']
        )


class ProfileHttp(F5Base):

    @logger
    def get_list(self):
        profiles = self._lb._channel.LocalLB.ProfileHttp.get_list()
        return profiles

    @logger
    def create(self, **kwargs):
        self._lb._channel.LocalLB.ProfileHttp.create(
            profile_names=kwargs['profile_names'])


class ProfileFastL4(F5Base):

    @logger
    def get_list(self):
        profiles = self._lb._channel.LocalLB.ProfileFastL4.get_list()
        return profiles

    @logger
    def create(self, **kwargs):
        self._lb._channel.LocalLB.ProfileFastL4.create(
            profile_names=kwargs['profile_names'])

    @logger
    def set_idle_timeout(self, **kwargs):
        self._lb._channel.LocalLB.ProfileFastL4.set_idle_timeout(
            profile_names=kwargs['profile_names'],
            timeouts=kwargs['timeouts']
        )

    @logger
    def set_loose_close_state(self, **kwargs):
        self._lb._channel.LocalLB.ProfileFastL4.set_loose_close_state(
            profile_names=kwargs['profile_names'],
            states=kwargs['states']
        )


class ProfileUDP(F5Base):

    @logger
    def get_list(self):
        profiles = self._lb._channel.LocalLB.ProfileUDP.get_list()
        return profiles

    @logger
    def create(self, **kwargs):
        self._lb._channel.LocalLB.ProfileUDP.create(
            profile_names=kwargs['profile_names'])

    @logger
    def set_idle_timeout(self, **kwargs):
        self._lb._channel.LocalLB.ProfileUDP.set_idle_timeout(
            profile_names=kwargs['profile_names'],
            timeouts=kwargs['timeouts']
        )
