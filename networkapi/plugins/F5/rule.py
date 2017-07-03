# -*- coding: utf-8 -*-
import logging

from networkapi.plugins.F5.f5base import F5Base
from networkapi.plugins.F5.util import logger

log = logging.getLogger(__name__)


class Rule(F5Base):

    @logger
    def create(self, **kwargs):
        for k, v in kwargs.items():
            if v == []:
                return

        self._lb._channel.LocalLB.Rule.create(
            rules=kwargs['rules'])

    @logger
    def update(self, **kwargs):
        for k, v in kwargs.items():
            if v == []:
                return

        self._lb._channel.LocalLB.Rule.modify_rule(
            rules=kwargs['rules'])

    @logger
    def delete(self, **kwargs):
        for k, v in kwargs.items():
            if v == []:
                return

        self._lb._channel.LocalLB.Rule.delete_rule(
            rule_names=kwargs['rule_names'])

    @logger
    def get(self, **kwargs):
        for k, v in kwargs.items():
            if v == []:
                return

        rules = self._lb._channel.LocalLB.Rule.query_rule(
            rule_names=kwargs['rule_names'])
        return rules

    @logger
    def list(self):
        rules = self._lb._channel.LocalLB.Rule.get_list()
        return rules
