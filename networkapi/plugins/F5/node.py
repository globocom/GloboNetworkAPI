import logging

from networkapi.plugins.F5.f5base import F5Base


log = logging.getLogger(__name__)


class Node(F5Base):

    def set_monitor_rule(self, **kwargs):
        log.info('pool:set_monitor_rule:%s' % kwargs)
        for k, v in kwargs.items():
            if v == []:
                return

        self._lb._channel.LocalLB.NodeAddressV2.set_monitor_rule(
            nodes=kwargs['nodes'],
            monitor_rules=kwargs['monitor_rules'])
