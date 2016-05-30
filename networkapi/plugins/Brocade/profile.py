# -*- coding: utf-8 -*-
import logging

from networkapi.plugins.Brocade.base import Base

log = logging.getLogger(__name__)


class ProfileTCP(Base):

    def get_list(self):
        profiles = self._lb._channel.LocalLB.ProfileTCP.get_list()
        return profiles

    def create(self, **kwargs):
        self._lb._channel.LocalLB.ProfileTCP.create(profile_names=kwargs['profile_names'])

    def set_idle_timeout(self, **kwargs):
        self._lb._channel.LocalLB.ProfileTCP.set_idle_timeout(
            profile_names=kwargs['profile_names'],
            timeouts=kwargs['timeouts']
        )


class ProfileHttp(Base):

    def get_list(self):
        profiles = self._lb._channel.LocalLB.ProfileHttp.get_list()
        return profiles

    def create(self, **kwargs):
        self._lb._channel.LocalLB.ProfileHttp.create(profile_names=kwargs['profile_names'])


class ProfileFastL4(Base):

    def get_list(self):
        profiles = self._lb._channel.LocalLB.ProfileFastL4.get_list()
        return profiles

    def create(self, **kwargs):
        self._lb._channel.LocalLB.ProfileFastL4.create(profile_names=kwargs['profile_names'])

    def set_idle_timeout(self, **kwargs):
        self._lb._channel.LocalLB.ProfileFastL4.set_idle_timeout(
            profile_names=kwargs['profile_names'],
            timeouts=kwargs['timeouts']
        )


class ProfileUDP(Base):

    def get_list(self):
        profiles = self._lb._channel.LocalLB.ProfileUDP.get_list()
        return profiles

    def create(self, **kwargs):
        self._lb._channel.LocalLB.ProfileUDP.create(profile_names=kwargs['profile_names'])

    def set_idle_timeout(self, **kwargs):
        self._lb._channel.LocalLB.ProfileUDP.set_idle_timeout(
            profile_names=kwargs['profile_names'],
            timeouts=kwargs['timeouts']
        )
