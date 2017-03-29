# -*- coding: utf-8 -*-
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

import logging
import requests

from networkapi.plugins import exceptions
from networkapi.equipamento.models import EquipamentoAcesso

log = logging.getLogger(__name__)

class BaseSdnPlugin(object):
    """
    Plugin base para interação com controlador SDN
    """
    protocol='http'

    def __init__(self, **kwargs):
        #Params and default values
        params = {
                    'equipment': None,
                    'equipment_access': None,
                    'protocol': 'https',
        }

        #Setting params via kwargs or use the defaults
        for param in params:
            if param in kwargs:
                setattr(self, param, kwargs.get(param))
            else:
                setattr(self, param, params.get(param))


    def _get_auth(self):
        raise NotImplementedError()

    def _get_host(self):

        if not hasattr(self, 'host'):

            if not hasattr(self, 'equipment_access') or self.equipment_access == None:
                log.error('No fqdn could be found for equipment %s .' %
                          (self.equipment.nome))
                raise exceptions.InvalidEquipmentAccessException()

            self.host = self.equipment_access.fqdn.strip()
            if self.host.find('://')<0:
                self.host = self.protocol + '://' + self.host

        return self.host

    def _get_uri(self, host=None, path=""):

        if not hasattr(self, 'uri'):
            if host==None:
                host=self._get_host()

            host = host.strip()
            path = path.strip()

            if host[ len(host)-1 ] == '/':
                host = host[0:len(host)-1]
            if path[0] == '/':
                path = path[1:len(path)]
            self.uri = host + '/' + path

        return self.uri

    def _get_headers(self, contentType):
        types = {
            'json': 'application/json',
            'xml':  'application/xml',
            'text': 'text/plain'
        }

        return {'content-type': types[contentType]}


