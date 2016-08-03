# -*- coding:utf-8 -*-
import logging

from networkapi.plugins.F5.f5base import F5Base
from networkapi.plugins.F5.util import logger

log = logging.getLogger(__name__)


class Pool(F5Base):

    @logger
    def create(self, **kwargs):
        for k, v in kwargs.items():
            if v == []:
                return

        self._lb._channel.LocalLB.Pool.create_v2(
            kwargs['names'],
            kwargs['lbmethod'],
            kwargs['members'])

    @logger
    def delete(self, **kwargs):
        for k, v in kwargs.items():
            if v == []:
                return

        self._lb._channel.LocalLB.Pool.delete_pool(
            kwargs['names'])

    @logger
    def set_service_down_action(self, **kwargs):
        for k, v in kwargs.items():
            if v == []:
                return

        self._lb._channel.LocalLB.Pool.set_action_on_service_down(
            kwargs['names'],
            kwargs['actions']
        )

    @logger
    def set_lb_method(self, **kwargs):
        for k, v in kwargs.items():
            if v == []:
                return

        self._lb._channel.LocalLB.Pool.set_lb_method(
            kwargs['names'],
            kwargs['lbmethod'])

    @logger
    def set_monitor_association(self, **kwargs):
        for k, v in kwargs.items():
            if v == []:
                return

        self._lb._channel.LocalLB.Pool.set_monitor_association(
            monitor_associations=kwargs['monitor_associations'])

    @logger
    def remove_monitor_association(self, **kwargs):
        for k, v in kwargs.items():
            if v == []:
                return

        self._lb._channel.LocalLB.Pool.remove_monitor_association(pool_names=kwargs['names'])

    @logger
    def get_monitor_association(self, **kwargs):
        for k, v in kwargs.items():
            if v == []:
                return

        monitor_associations = self._lb._channel.LocalLB.Pool.get_monitor_association(
            pool_names=kwargs['names'])

        return monitor_associations

    @logger
    def set_server_ip_tos(self, **kwargs):
        self._lb._channel.LocalLB.Pool.set_server_ip_tos(
            pool_names=kwargs['pool_names'],
            values=kwargs['values'])

    @logger
    def get_list(self):
        list_pool = self._lb._channel.LocalLB.Pool.get_list()
        return list_pool
