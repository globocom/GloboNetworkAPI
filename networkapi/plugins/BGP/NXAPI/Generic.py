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

    def create_neighbor(self, **kwargs):
        commands = []

        if kwargs['local_as']:
            cmd = 'router bgp {local_as}'.format(remote_as=kwargs['local_as'])
            commands.append(cmd)
        else:
            raise Exception('Local AS is needed.')

        if kwargs['vrf']:
            cmd = 'vrf {vrf}'.format(vrf=kwargs['vrf'])
            commands.append(cmd)
        else:
            raise Exception('VRF is needed.')

        if kwargs['remote_ip']:
            if kwargs['remote_as']:
                cmd = 'neighbor {remote_ip} remote-as {remote_as}'.format(
                    remote_ip=kwargs['remote_ip'],
                    remote_as=kwargs['remote_as'])
                commands.append(cmd)
            else:
                raise Exception('Remote AS is needed.')
        else:
            raise Exception('Remote Ip is needed.')

        if kwargs['description']:
            cmd = 'description {description}'.format(
                description=kwargs['description'])
            commands.append(cmd)
        else:
            raise Exception('Description is needed.')

        cmd = 'dynamic-capability'

        if kwargs['virtual_interface']:
            cmd = 'update-source {virtual_interface}'.format(
                virtual_interface=kwargs['virtual_interface'])
            commands.append(cmd)
        else:
            raise Exception('Interface is needed.')

        if kwargs['timers']:
            cmd = 'timers {timer_keepalive}'.format(
                timer_keepalive=kwargs['timer_keepalive'])
            if kwargs['timers']:
                cmd += ' {timer_timeout}'.format(
                    timer_timeout=kwargs['timer_timeout'])
                commands.append(cmd)
            else:
                raise Exception('Timer timeout is needed.')
        else:
            raise Exception('Keep alive is needed.')

        if kwargs['password']:
            cmd = 'password {password}'.format(password=kwargs['password'])
            commands.append(cmd)

        if kwargs['maximum_hops']:
            cmd = 'maximum-hops {maximum_hops}'.format(
                maximum_hops=kwargs['maximum_hops'])
            commands.append(cmd)

        cmd = 'address-family {address_family} unicast'.format(
            address_family=kwargs['address_family'])

        if kwargs['route_map_in']:
            'route-map {route_map_in} in'.format(
                route_map_in=kwargs['route_map_in'])

        if kwargs['route_map_out']:
            'route-map {route_map_out} out'.format(
                route_map_out=kwargs['route_map_out'])

        if kwargs['community']:
            cmd = 'send-community both'
            commands.append(cmd)

        if kwargs['remove_private_as']:
            cmd = 'remove-private-as'
            commands.append(cmd)

        if kwargs['next_hop_self']:
            cmd = 'next-hop-self'
            commands.append(cmd)

        cmd = 'next-hop-third-party'

        if kwargs['soft_reconfiguration']:
            cmd = 'soft-reconfiguration inbound'
            commands.append(cmd)

        payload = json.dumps(self._contruct(commands))

        self._request(data=payload,
                      contentType='json-rpc', path='ins')

    def delete_neighbor(self, kwargs):

        commands = []

        if kwargs['local_as']:
            cmd = 'router bgp {local_as}'.format(remote_as=kwargs['local_as'])
            commands.append(cmd)
        else:
            raise Exception('Local AS is needed.')

        if kwargs['vrf']:
            cmd = 'vrf {vrf}'.format(vrf=kwargs['vrf'])
            commands.append(cmd)
        else:
            raise Exception('VRF is needed.')

        if kwargs['remote_ip']:
            if kwargs['remote_as']:
                cmd = 'no neighbor {remote_ip} remote-as {remote_as}'.format(
                    remote_ip=kwargs['remote_ip'],
                    remote_as=kwargs['remote_as'])
                commands.append(cmd)
            else:
                raise Exception('Remote AS is needed.')
        else:
            raise Exception('Remote Ip is needed.')

        payload = json.dumps(self._contruct(commands))

        self._request(data=payload,
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
            request = requests.post(
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
