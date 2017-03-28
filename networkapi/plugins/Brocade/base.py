# -*- coding: utf-8 -*-
import logging

from networkapi.plugins import exceptions as base_exceptions
from networkapi.plugins.Brocade import lb

log = logging.getLogger(__name__)


class Base(object):

    def __init__(self, _lb=None):
        if _lb is not None and not isinstance(_lb, lb.Lb):
            raise base_exceptions.PluginUninstanced(
                'lb must be of type Brocade.Lb')

        self._lb = _lb
