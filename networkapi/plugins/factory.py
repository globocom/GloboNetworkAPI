# -*- coding:utf-8 -*-

# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from networkapi.api_rest import exceptions as api_exceptions
import logging
from networkapi.plugins import exceptions
import re

log = logging.getLogger(__name__)


class PluginFactory(object):

    @classmethod
    def plugin_exists(self, **kwargs):

        try:
            self.get_plugin(kwargs)
            return True
        except NotImplementedError:
            return False

    @classmethod
    def get_plugin(self, **kwargs):
        if 'modelo' in kwargs:
            modelo = kwargs.get('modelo')

            # TODO create a table in networkapi to specify wich plugin to load for
            # each equipment configuration
            if re.search('NEXUS', modelo.upper(), re.DOTALL):
                from .Cisco.NXOS.plugin import NXOS
                return NXOS
            if re.search('WS-|C65', modelo.upper(), re.DOTALL):
                from .Cisco.IOS.plugin import IOS
                return IOS

        if 'marca' in kwargs:
            marca = kwargs.get('marca')
            if re.search('HUAWEI', marca.upper(), re.DOTALL):
                from .Huawei import Generic
                return Generic
            if re.search('F5', marca.upper(), re.DOTALL):
                from .F5.Generic import Generic
                return Generic
            if re.search('BROCADE', marca.upper(), re.DOTALL) or re.search('FOUNDRY', marca.upper(), re.DOTALL):
                from .Brocade.Generic import Generic
                return Generic
            if re.search('DELL', marca.upper(), re.DOTALL):
                from .Dell.FTOS.plugin import FTOS
                return FTOS

        raise NotImplementedError()

    @classmethod
    def factory(self, equipment):

        marca = equipment.modelo.marca.nome
        modelo = equipment.modelo.nome
        plugin_name = self.get_plugin(modelo=modelo, marca=marca)

        return plugin_name(equipment=equipment)
