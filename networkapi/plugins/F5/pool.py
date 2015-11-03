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
        self._lb._channel.LocalLB.Pool.create_v2(
            kwargs['names'],
            kwargs['lbmethod'],
            kwargs['members'])

    def setServiceDownAction(self, **kwargs):
        self._lb._channel.LocalLB.Pool.set_action_on_service_down(
            kwargs['names'],
            kwargs['actions']
        )

    def setMonitorAssociation(self, **kwargs):
        monitor_associations = []

        for i, pool in enumerate(kwargs['names']):
            monitor_association = {
                'pool_name': None,
                'monitor_rule': {
                    'monitor_templates': None,
                    'type': None,
                    'quorum': None
                }
            }

            monitor_association['pool_name'] = kwargs['names'][i]

            if isinstance(kwargs['healthcheck'], str):
                monitor_templates = [kwargs['healthcheck'].lower()]
            else:
                monitor_templates = [h.lower() for h in kwargs['healthcheck']]

            monitor_association['monitor_rule'][
                'monitor_templates'] = monitor_templates

            monitor_association['monitor_rule'][
                'type'] = 'MONITOR_RULE_TYPE_SINGLE'

            monitor_association['monitor_rule']['quorum'] = 0

            monitor_associations.append(monitor_association)

        self._lb._channel.LocalLB.Pool.set_monitor_association(
            monitor_associations=monitor_associations)
