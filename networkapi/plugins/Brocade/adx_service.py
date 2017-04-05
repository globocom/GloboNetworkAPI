# -*- coding: utf-8 -*-
# Copyright 2014 Brocade Communications Systems, Inc.  All rights reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         https://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
#
import base64
import logging
import StringIO
import time

import httplib2
from suds import client as suds_client
from suds import transport as suds_transport
from suds.plugin import MessagePlugin
from suds.sax import element as suds_element


LOG = logging.getLogger(__name__)


class RemoveEmptyTags(MessagePlugin):

    def marshalled(self, context):
        context.envelope[1].prune()


class ClientCache:

    _ADX_SERVICE_CLIENTS = dict()

    @classmethod
    def add_adx_service_client(cls, device):
        LOG.debug('add_adx_service_client to dictionary')
        ip = device['management_ip']
        user = device['user']
        password = device['password']

        if ip not in cls._ADX_SERVICE_CLIENTS:
            adxslbservice = AdxService(ip, user, password)
            slb_service_client = adxslbservice.create_slb_service_client()

            adx_sys_service = AdxService(ip, user, password)
            sys_service_client = adx_sys_service.create_sys_service_client()

            adx_net_service = AdxService(ip, user, password)
            net_service_client = adx_net_service.create_net_service_client()

            cls._ADX_SERVICE_CLIENTS[ip] = [slb_service_client,
                                            sys_service_client,
                                            net_service_client]

    @classmethod
    def delete_adx_service_client(cls, device):
        LOG.debug('delete_adx_service_client from dictionary')
        ip = device['management_ip']
        if ip in cls._ADX_SERVICE_CLIENTS:
            del cls._ADX_SERVICE_CLIENTS[ip]

    @classmethod
    def get_adx_service_client(cls, device):
        LOG.debug('get_adx_service_client')
        ip = device['management_ip']

        if ip not in cls._ADX_SERVICE_CLIENTS:
            LOG.debug('Adx Service Client not yet initialized ...')
            cls.add_adx_service_client(device)

        return cls._ADX_SERVICE_CLIENTS[ip]


class Httplib2Response:
    pass


class Httplib2Transport(suds_transport.Transport):

    def __init__(self, **kwargs):
        self.username = kwargs['username']
        self.password = kwargs['password']
        suds_transport.Transport.__init__(self)
        self.http = httplib2.Http(disable_ssl_certificate_validation=True)

    def credentials(self):
        return (self.username, self.password)

    def add_credentials(self, request):
        credentials = self.credentials()
        if not (None in credentials):
            encoded = base64.encodestring(':'.join(credentials))
            basic = 'Basic %s' % encoded[:-1]
            request.headers['Authorization'] = basic

    def open(self, request):
        response = Httplib2Response()
        response.headers, response.message = (self.http.request
                                              (request.url,
                                               'GET',
                                               body=request.message,
                                               headers=request.headers))
        return StringIO.StringIO(response.message)

    def send(self, request):
        self.add_credentials(request)
        url = request.url
        message = request.message
        headers = request.headers
        response = Httplib2Response()
        response.headers, response.message = (self.http.request
                                              (url,
                                               'POST',
                                               body=message,
                                               headers=headers))
        return response


class AdxService:

    """ADX Service Initialization Class"""

    ns0 = ('ns0', 'https://schemas.xmlsoap.org/soap/envelope123/')

    def __init__(self, adx_ip_address, user_name, password, timeout=300):
        self.adx_ip_address = adx_ip_address
        self.user_name = user_name
        self.timeout = timeout
        self.password = password
        self.wsdl_base = 'https://' + adx_ip_address + '/wsdl/'
        self.sys_service_wsdl = 'sys_service.wsdl'
        self.slb_service_wsdl = 'slb_service.wsdl'
        self.net_service_wsdl = 'network_service.wsdl'
        self.location = 'https://' + adx_ip_address + '/WS/SYS'
        self.transport = Httplib2Transport(username=self.user_name,
                                           password=self.password)

    def create_slb_service_client(self):
        def soap_header():
            request_header = suds_element.Element('RequestHeader',
                                                  ns=AdxService.ns0)
            context = suds_element.Element('context').setText('default')
            request_header.append(context)
            return request_header

        url = self.wsdl_base + self.slb_service_wsdl
        location = 'https://' + self.adx_ip_address + '/WS/SLB'
        start = time.time()
        client = suds_client.Client(url, transport=self.transport,
                                    service='AdcSlb',
                                    location=location, timeout=self.timeout,
                                    plugins=[RemoveEmptyTags()])
        elapsed = (time.time() - start)
        LOG.debug('Time to initialize SLB Service Client: %s', elapsed)

        request_header = soap_header()
        client.set_options(soapheaders=request_header)
        return client

    def create_sys_service_client(self):
        def soap_header():
            request_header = suds_element.Element('RequestHeader',
                                                  ns=AdxService.ns0)
            context = suds_element.Element('context').setText('default')
            request_header.append(context)
            return request_header

        url = self.wsdl_base + self.sys_service_wsdl
        location = 'https://' + self.adx_ip_address + '/WS/SYS'
        start = time.time()
        client = suds_client.Client(url, transport=self.transport,
                                    service='AdcSysInfo',
                                    location=location, timeout=self.timeout,
                                    plugins=[RemoveEmptyTags()])
        elapsed = (time.time() - start)
        LOG.debug('Time to initialize SYS Service Client: %s', elapsed)

        request_header = soap_header()
        client.set_options(soapheaders=request_header)
        return client

    def create_net_service_client(self):
        def soap_header():
            request_header = suds_element.Element('RequestHeader',
                                                  ns=AdxService.ns0)
            context = suds_element.Element('context').setText('default')
            request_header.append(context)
            return request_header

        url = self.wsdl_base + self.net_service_wsdl
        location = 'https://' + self.adx_ip_address + '/WS/NET'
        start = time.time()
        client = suds_client.Client(url, transport=self.transport,
                                    service='AdcNet',
                                    location=location,
                                    timeout=self.timeout,
                                    plugins=[RemoveEmptyTags()])
        elapsed = (time.time() - start)
        LOG.debug('Time to initialize NET Service Client: %s', elapsed)

        request_header = soap_header()
        client.set_options(soapheaders=request_header)
        return client
