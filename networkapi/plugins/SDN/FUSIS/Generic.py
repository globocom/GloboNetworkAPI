# -*- coding: utf-8 -*-
"""
   Copyright 2017 Globo.com

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""
import json

import requests

from networkapi.plugins.SDN.base import BaseSdnPlugin
from networkapi.plugins.SDN.FUSIS import util


class Generic(BaseSdnPlugin):

    # VIPS
    @util.logger
    def create_vip(self, vips):
        for vip in vips['vips']:
            vip = vip['vip_request']
            service = {
                'address': vip['ipv4']['ip_formated'],
                'persistent': int(vip['options']['timeout']['nome_opcao_txt']),
                'mode': 'nat'
            }

            for port in vip['ports']:
                service['name'] = port['identifier']
                service['port'] = port['port']
                service['protocol'] = port['options'][
                    'l4_protocol']['nome_opcao_txt'].lower()

                for pool in port['pools']:
                    service['scheduler'] = \
                        self._get_scheduler(pool['server_pool']['lb_method'])

                    self._create_service(service)

                    for member in pool['server_pool']['pools_members']:
                        name = '{}_{}'.format(member['ip'], member['port'])
                        destination = {
                            'name': name,
                            'port': member['port'],
                            'address': member['ip'],
                            'weight': member['weight']
                        }
                        self._create_destination(service['name'], destination)

    def delete_vip(self, vips):
        pools_id = []
        for vip in vips['vips']:
            vip = vip['vip_request']
            for port in vip['ports']:
                for pool in port['pools']:
                    pools_id.append(pool['server_pool']['id'])
                    # Check if need
                    # for member in pool['server_pool']['pools_members']:
                    #     name = '{}_{}'.format(member['ip'], member['port'])
                    #     self._delete_destination(port['identifier'], name)
                self._delete_service(port['identifier'])
        return pools_id

    def update_vip(self, vips):

        pools_del = []
        pools_ins = []
        for vip in vips['vips']:
            vip = vip['vip_request']
            service = {
                'address': vip['ipv4']['ip_formated'],
                'persistent': int(vip['options']['timeout']['nome_opcao_txt']),
                'mode': 'nat'
            }

            for port in vip['ports']:
                if port.get('insert'):
                    service['name'] = port['identifier']
                    service['port'] = port['port']
                    service['protocol'] = port['options'][
                        'l4_protocol']['nome_opcao_txt'].lower()

                    for pool in port['pools']:
                        service['scheduler'] = \
                            self._get_scheduler(
                                pool['server_pool']['lb_method'])

                        self._create_service(service)

                        for member in pool['server_pool']['pools_members']:
                            name = '{}_{}'.format(member['ip'], member['port'])
                            destination = {
                                'name': name,
                                'port': member['port'],
                                'address': member['ip'],
                                'weight': member['weight']
                            }
                            self._create_destination(
                                service['name'], destination)
                elif port.get('delete'):
                    for pool in port['pools']:
                        if pool['server_pool']['id'] not in pools_del:
                            pools_del.append(pool['server_pool']['id'])
                    self._delete_service(port['identifier'])
                else:
                    for pool in port['pools']:
                        if pool['server_pool']['id'] not in pools_ins:
                            pools_ins.append(pool['server_pool']['id'])
                        if pool.get('delete'):
                            for member in pool['server_pool']['pools_members']:
                                name = '{}_{}'.format(
                                    member['ip'], member['port'])
                                self._delete_destination(
                                    port['identifier'], name)
                        elif pool.get('insert'):
                            for member in pool['server_pool']['pools_members']:
                                name = '{}_{}'.format(
                                    member['ip'], member['port'])
                                destination = {
                                    'name': name,
                                    'port': member['port'],
                                    'address': member['ip'],
                                    'weight': member['weight']
                                }
                                self._create_destination(
                                    service['name'], destination)

        pools_del = list(set(pools_del) - set(pools_ins))
        return pools_ins, pools_del

    @util.logger
    def get_name_eqpt(self, obj, port):
        name_vip = 'VIP_%s_%s' % (obj.id, port)

        return name_vip

    # POOL
    def create_pool(self, pools):
        raise Exception(
            'Pool can not be deploy in Fusis. Try deploy a VIP first.')

    def delete_pool(self, pools):
        raise Exception(
            'Pool can not be deploy in Fusis. Try undeploy a VIP first.')

    def update_pool(self, pools):

        for pool in pools['pools']:
            for vip in pool['vips']:
                for port in vip['ports']:
                    for pl in port['pools']:
                        if pl['server_pool']['id'] == pool['id']:
                            for member in pool['pools_members']:
                                name = '{}_{}'.format(
                                    member['ip'], member['port'])

                                if member.get('remove'):
                                    self._delete_destination(
                                        port['identifier'], name)
                                elif member.get('new'):
                                    destination = {
                                        'name': name,
                                        'port': member['port'],
                                        'address': member['ip'],
                                        'weight': member['weight']
                                    }
                                    self._create_destination(
                                        port['identifier'], destination)

    def _get_scheduler(self, scheduler):

        if scheduler == 'least-conn':
            return 'lc'
        elif scheduler == 'weighted':
            return 'wrr'
        elif scheduler == 'uri hash':
            return 'dh'
        elif scheduler == 'round-robin':
            return 'rr'

    def _get_service(self, name_service):

        url = 'services/{}'.format(name_service)

        return self._request(url, 'GET')

    def _get_destination(self, name_service, name_destination):

        url = 'services/{}/destinations/{}'.format(name_service,
                                                   name_destination)
        return self._request(url, 'GET')

    def _create_service(self, service_dict):

        url = 'services'

        self._request(url, 'POST', service_dict)

    def _create_destination(self, name_service, destination_dict):

        url = 'services/{}/destinations'.format(name_service)

        self._request(url, 'POST', destination_dict)

    def _delete_service(self, name_service):

        url = 'services/{}'.format(name_service)

        self._request(url, 'DELETE')

    def _delete_destination(self, name_service, name_destination):

        url = 'services/{}/destinations/{}'.format(name_service,
                                                   name_destination)
        self._request(url, 'DELETE')

    @util.logger
    def _request(self, url, method, payload=None):

        uri = 'http://10.224.142.239:8000/'

        method = method.lower()

        request_type_func = getattr(requests, method)

        request = request_type_func(
            uri + url,
            json=payload
        )
        request.raise_for_status()

        if request.text:
            return json.loads(request.text)
        return {}
