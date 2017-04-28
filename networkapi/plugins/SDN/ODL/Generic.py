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
from enum import Enum

import requests
from requests.auth import HTTPBasicAuth
from requests.exceptions import HTTPError

from networkapi.plugins import exceptions
from networkapi.plugins.SDN.base import BaseSdnPlugin
from networkapi.equipamento.models import EquipamentoAcesso
from networkapi.plugins.SDN.ODL.flows.acl import AclFlowBuilder

log = logging.getLogger(__name__)


class ODLPlugin(BaseSdnPlugin):
    """
    Plugin base para interação com controlador ODL
    """

    class FlowTypes(Enum):
        """ Inner class that holds the Enumeration of flow types """
        ACL = 0

    def __init__(self, **kwargs):

        super(ODLPlugin, self).__init__(**kwargs)

        try:
            if not isinstance(self.equipment_access, EquipamentoAcesso):
                log.info('equipment_access is not of EquipamentoAcesso type')
                raise TypeError

        except AttributeError, TypeError:
            # If AttributeError raised, equipment_access not exists as variable is this class
            self.equipment_access = self._get_equipment_access()


        print self.equipment_access
        print type(self.equipment_access)

    def get_flows(self):
        """
        
        :return: All flows for table 0 
        """
        nodes_ids = self._get_nodes_ids()

        for node_id in nodes_ids:
            path = "/restconf/config/opendaylight-inventory:nodes/node/%s/flow-node-inventory:table/0/"\
                   % (node_id)
            #TODO: Tratar retornos dos varios vSwitches
            retorno =  self._request(method="get", path=path, contentType='json')
            flows_list = retorno["flow-node-inventory:table"][0]
            #return AclFlowBuilder.dump(flows_list)
            # we are assuming that all bridges have the same content, so we return the fist occurrence for gets
            return flows_list

        flows_return = {}

    def add_flow(self, data=None, flow_id=0):
        builder = AclFlowBuilder(data)
        data_to_send = builder.dump()
        flow_id = builder.flows['flow'][0]['id']
        return self._flow(flow_id=flow_id, method='put', data=data_to_send)

    def del_flow(self, flow_id=0):
        return self._flow(flow_id=flow_id, method='delete')

    def get_flow(self, flow_id=0):
        return self._flow(flow_id=flow_id, method='get')

    def _flow(self, flow_id=0, method='', data=None):

        allowed_methods=["get", "put", "delete"]

        if flow_id < 1 or method not in allowed_methods:
            log.error("Invalid parameters in OLDPlugin flow handler")
            raise exceptions.ValueInvalid()

        nodes_ids = self._get_nodes_ids()

        for node_id in nodes_ids:
            path = "/restconf/config/opendaylight-inventory:nodes/node/%s/flow-node-inventory:table/0/flow/%s" \
                   % (node_id, flow_id)

            # TODO: Tratar retornos dos varios vSwitches
            retorno = self._request(method=method, path=path, data=data, contentType='json')

            #we are assuming that all bridges have the same content, so we return the fist occurrence for gets
            if method=='get':
                return retorno["flow-node-inventory:flow"][0]

        return retorno



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
                params[param] = kwargs.get(param)

        headers = self._get_headers(contentType=params["contentType"])
        uri = self._get_uri(path=params["path"])

        log.info("Starting %s request to controller %s at %s. Data to be sent: %s" %
                    (params["method"], self.equipment.nome, params["path"], params["data"])
                 )



        try:
            func = getattr(requests, params["method"])  # Raises AttributeError if method is not valid
            request = func(
                uri,
                auth=self._get_auth(),
                headers=headers,
                verify=params["verify"],
                data=params["data"]
            )

            request.raise_for_status()

            try:
                return json.loads(request.text)
            except:
                return

        except AttributeError:
            log.error('Request method must be valid HTTP request. '
                      'ie: GET, POST, PUT, DELETE')
        except HTTPError:
            try:
                response = json.loads(request.text)
                for error in response["errors"]["error"]:
                    log.error(error["error-message"])
            except:
                log.error("Unknown error during request to ODL Controller")
            raise exceptions.CommandErrorException(msg=request.status_code)

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

        return {'content-type': types[contentType],
                'Accept': types[contentType]}

    def _get_equipment_access(self):
        try:
            return EquipamentoAcesso.search(
                None, self.equipment, 'https').uniqueResult()
        except Exception, e:
            log.error('Access type %s not found for equipment %s.' %
                      ('https', self.equipment.nome))
            raise exceptions.InvalidEquipmentAccessException()
        #TODO: ver o metodo existente, bater com o host (http com http)
