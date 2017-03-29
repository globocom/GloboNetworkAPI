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
import requests
from requests.auth import HTTPBasicAuth
from requests.exceptions import HTTPError

from networkapi.plugins import exceptions
from networkapi.plugins.SDN.base import BaseSdnPlugin
from networkapi.equipamento.models import EquipamentoAcesso

log = logging.getLogger(__name__)

class ODLPlugin(BaseSdnPlugin):
    """
    Plugin base para interação com controlador SDN
    """

    def __init__(self, **kwargs):

        super(ODLPlugin, self).__init__(**kwargs)

        if not hasattr(self, 'equipment_access') or self.equipment_access==None:
            self.equipment_Access = self._get_equipment_access()



    def add_flow(self, data):
        #TODO: como definir o flow id? onde guardar essa info? ou pegar essa info do controller?
        #TODO: como definir o controller id?
        path="/restconf/config/opendaylight-inventory:nodes/node/openflow:200920773006274/flow-node-inventory:table/0/flow/3"
        uri = self._get_uri(path=path)

        data = json.dumps(data).strip().replace(' ','') #remove qualquer espaço

        print data
        raise exceptions.APIException() #evitando enviar os flows para o controlador por enquanto

        return self._request(method=method, uri=uri, data=data, contentType='json')


    #TODO: Método abaixo é apenas uma viagem. devo remover.
    def act(self, action="", data=None, contentType='json'):
        actions={
            'get_nodes': {
                'path': '/restconf/config/opendaylight-inventory:nodes',
                'method': 'get',
                },
            'add_flow': {
                'path': '/restconf/config/opendaylight-inventory:nodes',
                'method': 'get',
                }
        }

        host = self._get_host()
        path = actions[action]["path"]
        uri = self._get_uri(host=host, path=path)
        method = actions[action]["method"]

        if data!=None:
            data=json.dump(data)
            data=data.strip()

        print data
        raise exceptions.APIException()

        return self._request(method=method, uri=uri, data=data, contentType=contentType)




    def _request(self, **kwargs):
        # Params and default values
        params = {
            'method': 'get',
            'uri': '',
            'data': None,
            'contentType': 'json',
            'verify': False
        }

        # Setting params via kwargs or use the defaults
        for param in params:
            if param in kwargs:
                params[param]= kwargs.get(param)

        headers = self._get_headers(contentType=params["contentType"])

        try:
            func = getattr(requests, params["method"]) #Raises AttributeError if method is not valid
            request = func(
                params["uri"],
                auth=self._get_auth(),
                headers=headers,
                verify=params["verify"],
                data=params["data"]
            )

            request.raise_for_status()

            if params["contentType"] == 'json':
                return json.loads(request.text)
            else:
                return request.text

        except AttributeError:
            self.logger.error('Request method must be valid HTTP request. ie: GET, POST, PUT, DELETE')
        except HTTPError:
            error = self._parse(request.text)
            self.logger.error(error)
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

        return {'content-type': types[contentType]}


    def _get_equipment_access(self):
        try:
            self.equipment_access = EquipamentoAcesso.search(
                None, self.equipment, 'https').uniqueResult()
        except Exception, e:
            log.error('Access type %s not found for equipment %s.' %
                      ('https', self.equipment.nome))
            raise exceptions.InvalidEquipmentAccessException()



