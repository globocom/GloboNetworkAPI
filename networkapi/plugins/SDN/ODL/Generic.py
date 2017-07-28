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

from django.core.exceptions import ObjectDoesNotExist

from networkapi.plugins import exceptions
from networkapi.plugins.SDN.base import BaseSdnPlugin
from networkapi.equipamento.models import EquipamentoAcesso
from networkapi.plugins.SDN.ODL.flows.acl import AclFlowBuilder

log = logging.getLogger(__name__)


class FlowTypes(Enum):
    """ Inner class that holds the Enumeration of flow types """
    ACL = 0


class ODLPlugin(BaseSdnPlugin):
    """
    Plugin base para interação com controlador ODL
    """

    def __init__(self, **kwargs):

        super(ODLPlugin, self).__init__(**kwargs)

        try:

            if not isinstance(self.equipment_access, EquipamentoAcesso):
                msg = 'equipment_access is not of EquipamentoAcesso type'
                log.info(msg)
                raise TypeError(msg)

        except (AttributeError, TypeError):
            # If AttributeError raised, equipment_access do not exists
            self.equipment_access = self._get_equipment_access()

    def add_flow(self, data=None, flow_id=0, flow_type=FlowTypes.ACL):

        if flow_type == FlowTypes.ACL:
            builder = AclFlowBuilder(data)

            flows_set = builder.build()

            for flows in flows_set:
                for flow in flows['flow']:

                    self._flow(flow_id=flow['id'],
                               method='put',
                               data=json.dumps({'flow': [flow]}))

        return None

    def del_flow(self, flow_id=0):
        return self._flow(flow_id=flow_id, method='delete')

    def flush_flows(self):
        nodes_ids = self._get_nodes_ids()
        if len(nodes_ids) < 1:
            raise exceptions.ControllerInventoryIsEmpty(msg="No nodes found")

        for node_id in nodes_ids:
            try:
                path = "/restconf/config/opendaylight-inventory:nodes/node/%s/flow-node-inventory:table/0/" \
                       % node_id

                self._request(
                        method="delete", path=path, contentType='json'
                    )
            except HTTPError as e:
                if e.response.status_code==404:
                    pass
                else:
                    raise exceptions.CommandErrorException(msh=self._parse_errors(e.response.json()))
            except Exception as e:
                raise e

    def _parse_errors(self, err_json):
        sep = ""
        msg = ""
        for error in err_json["errors"]["error"]:
            msg = msg + sep + error["error-message"]
            sep = ". "
        return msg

    def get_flow(self, flow_id=0):
        return self._flow(flow_id=flow_id, method='get')

    def _flow(self, flow_id=0, method='', data=None):

        allowed_methods = ["get", "put", "delete"]

        if flow_id < 1 or method not in allowed_methods:
            log.error("Invalid parameters in OLDPlugin flow handler")
            raise exceptions.ValueInvalid()

        nodes_ids = self._get_nodes_ids()
        if len(nodes_ids)<1:
            raise exceptions.ControllerInventoryIsEmpty(msg="No nodes found")

        return_flows = []
        for node_id in nodes_ids:
            path = "/restconf/config/opendaylight-inventory:nodes/node/%s/flow-node-inventory:table/0/flow/%s" \
                   % (node_id, flow_id)

            return_flows.append(
                self._request(
                    method=method, path=path, data=data, contentType='json'
                )
            )

        return return_flows

    def get_flows(self):
        """
        :return: All flows for table 0
        """
        nodes_ids = self._get_nodes_ids()
        if len(nodes_ids)<1:
            raise exceptions.ControllerInventoryIsEmpty(msg="No nodes found")

        flows_list_by_switch = {}
        for node_id in nodes_ids:
            try:
                path = "/restconf/config/opendaylight-inventory:nodes/node/%s/flow-node-inventory:table/0/"\
                       % (node_id)

                flows_list_by_switch[node_id] = self._request(method="get", path=path, contentType='json')["flow-node-inventory:table"]

            except HTTPError as e:
                if e.response.status_code == 404:
                    flows_list_by_switch[node_id] =[]
                else:
                    raise exceptions.CommandErrorException(msh=self._parse_errors(e.response.json()))
            except Exception as e:
                raise e


        return flows_list_by_switch
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
        path = "/restconf/config/opendaylight-inventory:nodes/"
        nodes = self._request(method='get', path=path, contentType='json')
        retorno = []
        if nodes['nodes'].has_key('node'):
            for node in nodes['nodes']['node']:
                if node["id"] not in ["controller-config"]:
                    retorno.append(node)
        return retorno

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

        # if isinstance(params["data"], basestring):
        #     params["data"] = params["data"].replace(" ","")

        headers = self._get_headers(contentType=params["contentType"])
        uri = self._get_uri(path=params["path"])

        log.debug(
            "Starting %s request to controller %s at %s. Data to be sent: %s" %
            (params["method"], self.equipment.nome, uri, params["data"])
        )

        try:
            # Raises AttributeError if method is not valid
            func = getattr(requests, params["method"])
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
        # except HTTPError as e:
        #
        #     try:
        #         response = json.loads(request.text)
        #         for error in response["errors"]["error"]:
        #             log.error(error["error-message"])
        #     except:
        #         log.error("Unknown error during request to ODL Controller")
        #
        #     raise HTTPError("Error during request to ODL Controller. Code %s" % request.status_code)

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

            access = None
            try:
                access = EquipamentoAcesso.search(
                    None, self.equipment, 'https').uniqueResult()
            except ObjectDoesNotExist:
                access = EquipamentoAcesso.search(
                    None, self.equipment, 'http').uniqueResult()
            return access

        except Exception:

            log.error('Access type %s not found for equipment %s.' %
                      ('https', self.equipment.nome))
            raise exceptions.InvalidEquipmentAccessException()
