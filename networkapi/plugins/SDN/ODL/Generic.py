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
import json
from io import BytesIO

import requests
from requests.auth import HTTPBasicAuth
from requests.exceptions import HTTPError

from networkapi.plugins import exceptions
from networkapi.plugins.SDN.base import BaseSdnPlugin
from networkapi.equipamento.models import EquipamentoAcesso

log = logging.getLogger(__name__)

#TODO: excpect always json

class ODLPlugin(BaseSdnPlugin):
    """
    Plugin base para interação com controlador SDN
    """

    def __init__(self, **kwargs):

        super(ODLPlugin, self).__init__(**kwargs)

        if not hasattr(self, 'equipment_access') or self.equipment_access==None:
            self.equipment_Access = self._get_equipment_access()




    def add_flow(self, data, flow_id):

        nodes_ids = self._get_nodes_ids()
        #TODO: Retirar a linha abaixo. Linha adicionada por conta do ambiente ter testes rodando em paralelo
        nodes_ids = ["openflow:134984912119576"]

        for node_id in nodes_ids:
            path="/restconf/config/opendaylight-inventory:nodes/node/%s/flow-node-inventory:table/0/flow/%d" \
                    % (node_id, flow_id)

            data = json.dumps(data).strip().replace(' ','') #remove qualquer espaço

            return self._request(method='post', path=path, data=data, contentType='json')


    def _get_nodes_ids(self):
        """
        Returns a list of nodes ids controlled by ODL
        """
        nodes = self._get_nodes()
        nodes_ids = []
        for node in nodes:
            nodes_ids.append(node["id"])
        return nodes_ids


    def _get_nodes(self):
        path="/restconf/operational/opendaylight-inventory:nodes/"
        nodes = self._request(method='get', path=path, contentType='json')
        return nodes['nodes']['node']


    def _request(self, **kwargs):
        # Params and default values
        params = {
            'method': 'get',
            'path': '',
            'data': None,
            'contentType': 'json',
            'verify': False
        }


        # Setting params via kwargs or use the defaults
        for param in params:
            if param in kwargs:
                params[param]= kwargs.get(param)

        headers = self._get_headers(contentType=params["contentType"])
        uri = self._get_uri(path=params["path"])

        try:
            func = getattr(requests, params["method"]) #Raises AttributeError if method is not valid
            request = func(
                uri,
                auth=self._get_auth(),
                headers=headers,
                verify=params["verify"],
                json=params["data"]
            )

            request.raise_for_status()

            if params["contentType"] == 'json':
                return json.loads(request.text)
            else:
                return request.text

        except AttributeError:
            log.error('Request method must be valid HTTP request. ie: GET, POST, PUT, DELETE')
        except HTTPError:
            try:
                response = json.loads(request.text)
                for error in response["errors"]["error"]:
                    log.error( error["error-message"] )
            except:
                log.error("Unknown error while making request to ODL Controller")
            raise exceptions.CommandErrorException()




    def _get_auth(self):
        return self._basic_auth()

    def _basic_auth(self):
        return HTTPBasicAuth(
            self.equipment_access.user,
            self.equipment_access.password
        )

    def _o_auth(self):
        pass


    def _get_headers(self, contentType):
        types = {
            'json': 'application/yang.data+json',
            'xml':  'application/xml',
            'text': 'text/plain'
        }

        return {'content-type': types[contentType], 'Accept': types[contentType]}


    def _get_equipment_access(self):
        try:
            self.equipment_access = EquipamentoAcesso.search(
                None, self.equipment, 'https').uniqueResult()
        except Exception, e:
            log.error('Access type %s not found for equipment %s.' %
                      ('https', self.equipment.nome))
            raise exceptions.InvalidEquipmentAccessException()



