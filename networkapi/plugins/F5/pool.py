from networkapi.plugins import F5
from networkapi.plugins.F5 import lb

from networkapi.plugins import exceptions as base_exceptions

import logging

log = logging.getLogger(__name__)


class Pool(object):

    def __init__(self, _lb=None):
        if _lb is not None and not isinstance(_lb, lb.Lb):
            raise base_exceptions.PluginUninstanced('lb must be of type F5.Lb')

        self._lb = _lb

    def create(self, **kwargs):
        for k, v in kwargs.items():
            if v == []:
                return

        self._lb._channel.LocalLB.Pool.create_v2(
            kwargs['names'],
            kwargs['lbmethod'],
            kwargs['members'])

    def delete(self, **kwargs):
        for k, v in kwargs.items():
            if v == []:
                return

        self._lb._channel.LocalLB.Pool.delete_pool(
            kwargs['names'])

    def setServiceDownAction(self, **kwargs):
        for k, v in kwargs.items():
            if v == []:
                return

        self._lb._channel.LocalLB.Pool.set_action_on_service_down(
            kwargs['names'],
            kwargs['actions']
        )

    def setLbMethod(self, **kwargs):
        for k, v in kwargs.items():
            if v == []:
                return

        self._lb._channel.LocalLB.Pool.set_lb_method(
            kwargs['names'],
            kwargs['lbmethod'])

    def setMonitorAssociation(self, **kwargs):
        for k, v in kwargs.items():
            if v == []:
                return

        self._lb._channel.LocalLB.Pool.set_monitor_association(
            monitor_associations=kwargs['monitor_associations'])

    def removeMonitorAssociation(self, **kwargs):
        for k, v in kwargs.items():
            if v == []:
                return

        self._lb._channel.LocalLB.Pool.remove_monitor_association(pool_names=kwargs['names'])

    def getMonitorAssociation(self, **kwargs):
        for k, v in kwargs.items():
            if v == []:
                return

        monitor_associations = self._lb._channel.LocalLB.Pool.get_monitor_association(
            pool_names=kwargs['names'])

        return monitor_associations
