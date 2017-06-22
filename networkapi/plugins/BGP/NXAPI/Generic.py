# -*- coding: utf-8 -*-
import json
import logging

import requests
from requests.auth import HTTPBasicAuth
from requests.exceptions import HTTPError

from networkapi.equipamento.models import EquipamentoAcesso
from networkapi.plugins import exceptions
from networkapi.plugins.BGP.base import BaseBgpPlugin

log = logging.getLogger(__name__)


class NxApiPlugin(BaseBgpPlugin):

    """Plugin base para interação com NX API."""

    protocol = 'http'

    def __init__(self, **kwargs):

        super(NxApiPlugin, self).__init__(**kwargs)

        self.equipment_access = self._get_equipment_access()

    def create_neighbor(self, as_number, vrf, ip_neighbor, as_neighbor,
                        description, interface, route_map_in, route_map_out):

        commands = [
            'router bgp {as_number}'.format(as_number=as_number),
            'vrf {vrf}'.format(vrf=vrf),
            'neighbor {ip_neighbor} remote-as {as_neighbor}'.format(
                ip_neighbor=ip_neighbor, as_neighbor=as_neighbor),
            'description {description}'.format(description=description),
            'dynamic-capability',
            'update-source {interface}'.format(interface=interface),
            'timers 60 180',
            'address-family ipv4 unicast',
            'route-map {route_map_in} in'.format(route_map_in=route_map_in),
            'route-map {route_map_out} out'.format(
                route_map_out=route_map_out),
            'send-community both',
            'next-hop-self',
            'next-hop-third-party',
            'soft-reconfiguration inbound'
        ]

        payload = json.dumps(self._contruct(commands))

        self._request(method='post', data=payload,
                      contentType='json-rpc', path='ins')

    def delete_neighbor(self, as_number, vrf, ip_neighbor, as_neighbor):

        commands = [
            'router bgp {as_number}'.format(as_number=as_number),
            'vrf {vrf}'.format(vrf=vrf),
            'no neighbor {ip_neighbor} remote-as {as_neighbor}'.format(
                ip_neighbor=ip_neighbor, as_neighbor=as_neighbor),
        ]

        payload = json.dumps(self._contruct(commands))

        self._request(method='post', data=payload,
                      contentType='json-rpc', path='ins')

    def _contruct(self, commands):

        payload = list()

        for index, command in enumerate(commands):

            payload.append({
                'jsonrpc': '2.0',
                'method': 'cli_ascii',
                'params': {
                    'cmd': command,
                    'version': 1.2
                },
                'id': index
            })

        return payload

    def _request(self, **kwargs):
        # Params and default values
        params = {
            'method': 'get',
            'path': '',
            'data': None,
            'contentType': 'json-rpc',
            'verify': False
        }

        # Setting params via kwargs or use the defaults
        for param in params:
            if param in kwargs:
                params[param] = kwargs.get(param)

        headers = self._get_headers(content_type=params['contentType'])
        uri = self._get_uri(path=params['path'])

        log.info(
            'Starting {method} request to NX-API {equipment} at {uri}.  \
            Data to be sent: {data}'.format(
                method=params['method'], equipment=self.equipment.nome,
                uri=uri, data=params['data']))

        try:
            # Raises AttributeError if method is not valid
            func = getattr(requests, params['method'])
            request = func(
                uri,
                auth=self._get_auth(),
                headers=headers,
                verify=params['verify'],
                data=params['data']
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
                for error in response['errors']['error']:
                    log.error(error['error-message'])
            except:
                log.error('Unknown error during request to NX-API')

            raise HTTPError(request.status_code)

    def _get_auth(self):
        return self._basic_auth()

    def _basic_auth(self):
        return HTTPBasicAuth(
            self.equipment_access.user,
            self.equipment_access.password
        )

    def _get_host(self):

        if not hasattr(self, 'host') or self.host is None:

            if not isinstance(self.equipment_access, EquipamentoAcesso):

                log.error(
                    'No fqdn could be found for equipment {equipment}.'.format(
                        equipment=self.equipment.nome))
                raise exceptions.InvalidEquipmentAccessException()

            self.host = self.equipment_access.fqdn.strip()
            if self.host.find('://') < 0:
                self.host = self.protocol + '://' + self.host

        return self.host

    def _get_uri(self, host=None, path='ins'):

        if host is None:
            host = self._get_host()

        host = host.strip()
        path = path.strip()

        if host[len(host) - 1] == '/':
            host = host[0:len(host) - 1]
        if path[0] == '/':
            path = path[1:len(path)]
        self.uri = host + '/' + path

        return self.uri

    def _get_headers(self, content_type):
        types = {
            'json-rpc': 'application/json-rpc'
        }

        return {'content-type': types[content_type]}

    def _get_equipment_access(self):
        try:
            return EquipamentoAcesso.search(
                None, self.equipment, 'http').uniqueResult()
        except Exception:
            log.error('Access type %s not found for equipment %s.' %
                      ('http', self.equipment.nome))
            raise exceptions.InvalidEquipmentAccessException()
