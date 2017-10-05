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
from networkapi.plugins.SDN.base import BaseSdnPlugin
import requests
import json

class Generic(BaseSdnPlugin):

    # VIPS
    def create_vip(self, vips):

        for vip in vips['vips']:
            service = {
                'address': vip['ipv4']['ip_formated'],
                'persistent': int(vip['options']['timeout']['nome_opcao_txt']),
                'mode': 'nat'
            }

            for port in vip['ports']:
                service['name'] =  '{}_{}'.format(vip['id'], port['port'])
                service['port'] = port['port']
                service['protocol'] = vip['options']['l4_protocol']\
                                        ['nome_opcao_txt'].lower()

                for pool in port['pools']:

                    service['scheduler'] = \
                        self._get_scheduler(pool['server_pool']['lb_method'])
                    self._create_service(service)


    def delete_vip(self, vips):

        for vip in vips['vips']:

            pass


    def update_vip(self, vips):

        pass


    # POOL
    def create_pool(self, pools):

        for vip in pools['vips']:

            name_service = vip['name']

            for port in vip['ports']:

                for pool in port['pools']:


        for pool in pools['server_pools']:

            for member in pool['server_pool_members']:
                destination = {
                    'name': member['identifier'],
                    'port': member['port_real'],
                    'host': member['ip']['ip_formated'],
                    'weight': member['weight']
                }
                name_service = ''
                self._create_destination(destination, name_service)

    def delete_pool(self, pools):

        for pool in pools['server_pools']:
            pass

    def update_pool(self, pools):

        pass

    def _get_scheduler(self, scheduler):

        if scheduler == 'least-conn':
            return 'lc'
        elif scheduler == 'weighted':
            return 'wrr' # check
        elif scheduler == 'uri hash':
            return 'dh' # check
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

        url = 'services/'

        self._request(url, 'POST', service_dict)

    def _create_destination(self, destination_dict, name_service):

        url = 'services/{}/destinations'.format(name_service)

        self._request(url, 'POST', destination_dict)

    def _delete_service(self, name_service):

        url = 'services/{}'.format(name_service)

        self._request(url, 'DELETE')

    def _delete_destination(self, name_service, name_destination):

        url = 'services/{}/destinations/{}'.format(name_service,
                                                   name_destination)
        self._request(url, 'DELETE')

    def _request(self, url, method, payload=None):

        uri = 'http://192.168.244.244:8000/'

        method = method.lower()

        request_type_func = getattr(requests, method)

        request = request_type_func(
            uri + url,
            json = payload
        )
        request.raise_for_status()

        return json.loads(request.text)

