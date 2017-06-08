# -*- coding: utf-8 -*-
import logging

from networkapi.plugins.F5.f5base import F5Base
from networkapi.plugins.F5.util import logger

log = logging.getLogger(__name__)


class Node(F5Base):

    @logger
    def set_monitor_rule(self, **kwargs):

        for k, v in kwargs.items():
            if v == []:
                return

        self._lb._channel.LocalLB.NodeAddressV2.set_monitor_rule(
            nodes=kwargs['monitor_associations']['nodes'],
            monitor_rules=kwargs['monitor_associations']['monitor_rules'])

    @logger
    def set_description(self, **kwargs):
        for k, v in kwargs.items():
            if v == []:
                return

        self._lb._channel.LocalLB.NodeAddressV2.set_description(
            nodes=kwargs['nodes'],
            descriptions=kwargs['descriptions'])
