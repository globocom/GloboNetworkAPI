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
import httplib

import pytest
from django.core import mail
from django.core.management import call_command
from django.db import connections
from django.db import DEFAULT_DB_ALIAS
from django.test import Client
from django.test import TransactionTestCase
from django.test.client import MULTIPART_CONTENT

from networkapi.test.assertions import *
from networkapi.test.functions import CodeError
from networkapi.test.functions import is_valid_attr
from networkapi.test.functions import valid_content
from networkapi.test.functions import valid_get_all
from networkapi.test.functions import valid_response
from networkapi.test.mock_scripts import *
from networkapi.test.utils import dict2xml
from networkapi.test.utils import load_json
from networkapi.test.utils import mock_login
from networkapi.test.utils import permute
from networkapi.test.utils import show_sql
from networkapi.test.utils import xml2dict
# exporting

skipTest = pytest.mark.skipTest
me = pytest.mark.me
bug = pytest.mark.bug

__all__ = ('log', 'show_sql', 'xml2dict', 'dict2xml', 'BasicTestCase', 'me',
           'skipTest', 'bug', 'mock_script', 'assert_response_error',
           'assert_response_success', 'permute')

log.info(u'Desligando logging de queries')
show_sql(False)

CONTENT_APPLICATION_XML = 'application/xml'


class CLIENT_TYPES():
    TEST = 'TEST'
    NO_PERMISSION = 'NO_PERMISSION'
    NO_WRITE_PERMISSION = 'NO_WRITE_PERMISSION'
    NO_READ_PERMISSION = 'NO_READ_PERMISSION'
    NO_ACTIVE = 'NO_ACTIVE'


class BasicTestCase(TransactionTestCase):

    URL_SAVE = ''
    URL_ALTER = ''
    URL_REMOVE = ''
    URL_GET_BY_ID = ''
    URL_GET_ALL = ''

    ID_NONEXISTENT = 9999

    @classmethod
    def setUpClass(cls):
        """
          Call static method to load fixtures once per class,
          making tests faster
        """
        cls._fixture_load()

    @classmethod
    def _fixture_load(cls):
        """
          Method used to load fixtures once for class, instead of once for test.
        """

        # If the test case has a multi_db=True flag, flush all databases.
        # Otherwise, just flush default.
        if getattr(cls, 'multi_db', False):
            databases = connections
        else:
            databases = [DEFAULT_DB_ALIAS]
        for db in databases:
            call_command('flush', verbosity=0, interactive=False, database=db)

            if hasattr(cls, 'fixtures'):
                # We have to use this slightly awkward syntax due to the fact
                # that we're using *args and **kwargs together.
                call_command(
                    'loaddata', *cls.fixtures, **{'verbosity': 0, 'database': db})

    def _pre_setup(self):
        """
          Overriding default method, to not load fixtures every test,
          since its done by the class now.

          Performs any pre-test setup. This includes:

          * If the Test Case class has a 'urls' member, replace the
            ROOT_URLCONF with it.
          * Clearing the mail test outbox.
        """
        # self._fixture_setup()
        self._urlconf_setup()
        mail.outbox = []

    def __init__(self, *args, **kargs):
        super(TransactionTestCase, self).__init__(*args, **kargs)
        self.client = NetworkAPITestClient()

    def client_autenticado(self, *perms):
        c = NetworkAPITestClient(
            HTTP_NETWORKAPI_USERNAME='TEST', HTTP_NETWORKAPI_PASSWORD='12345678')
        return c

    def client_no_permission(self, *perms):
        c = NetworkAPITestClient(
            HTTP_NETWORKAPI_USERNAME='NO_PERMISSION', HTTP_NETWORKAPI_PASSWORD='12345678')
        return c

    def client_no_write_permission(self, *perms):
        c = NetworkAPITestClient(
            HTTP_NETWORKAPI_USERNAME='NO_WRITE_PERMISSION', HTTP_NETWORKAPI_PASSWORD='12345678')
        return c

    def client_no_read_permission(self, *perms):
        c = NetworkAPITestClient(
            HTTP_NETWORKAPI_USERNAME='NO_READ_PERMISSION', HTTP_NETWORKAPI_PASSWORD='12345678')
        return c

    def client_no_active(self, *perms):
        c = NetworkAPITestClient(
            HTTP_NETWORKAPI_USERNAME='NO_ACTIVE', HTTP_NETWORKAPI_PASSWORD='12345678')
        return c

    def switch(self, client_type):

        client = None

        if client_type == CLIENT_TYPES.TEST:
            client = self.client_autenticado()

        elif client_type == CLIENT_TYPES.NO_PERMISSION:
            client = self.client_no_permission()

        elif client_type == CLIENT_TYPES.NO_WRITE_PERMISSION:
            client = self.client_no_write_permission()

        elif client_type == CLIENT_TYPES.NO_READ_PERMISSION:
            client = self.client_no_read_permission()

        elif client_type == CLIENT_TYPES.NO_ACTIVE:
            client = self.client_no_active()

        return client

    def save(self, dicts, client_type=CLIENT_TYPES.TEST):
        client = self.switch(client_type)
        response = client.postXML(self.URL_SAVE, dicts)
        return response

    def alter(self, idt, dicts, client_type=CLIENT_TYPES.TEST):
        client = self.switch(client_type)
        response = client.putXML(self.URL_ALTER % idt, dicts)
        return response

    def remove(self, idt, client_type=CLIENT_TYPES.TEST):
        client = self.switch(client_type)
        response = client.delete(self.URL_REMOVE % idt)
        return response

    def get_by_id(self, idt, client_type=CLIENT_TYPES.TEST):
        client = self.switch(client_type)
        response = client.get(self.URL_GET_BY_ID % idt)
        return response

    def get_all(self, client_type=CLIENT_TYPES.TEST):
        client = self.switch(client_type)
        response = client.get(self.URL_GET_ALL)
        return response


import urllib
from urlparse import urlparse, urlunparse, urlsplit
import sys
import os
import re
import mimetypes
import warnings
from copy import copy
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

from django.conf import settings
from django.contrib.auth import authenticate, login
from django.core.handlers.base import BaseHandler
from django.core.handlers.wsgi import WSGIRequest
from django.core.signals import got_request_exception
from django.http import SimpleCookie, HttpRequest, QueryDict
from django.template import TemplateDoesNotExist
from django.test import signals
from django.utils.functional import curry
from django.utils.encoding import smart_str
from django.utils.http import urlencode
from django.utils.importlib import import_module
from django.utils.itercompat import is_iterable
from django.db import transaction, close_connection
from django.test.utils import ContextList


class FakePayload(object):

    """
    A wrapper around StringIO that restricts what can be read since data from
    the network can't be seeked and cannot be read outside of its content
    length. This makes sure that views can't do anything under the test client
    that wouldn't work in Real Life.
    """

    def __init__(self, content):
        self.__content = StringIO(content)
        self.__len = len(content)

    def read(self, num_bytes=None):
        if num_bytes is None:
            num_bytes = self.__len or 0
        assert self.__len >= num_bytes, 'Cannot read more than the available bytes from the HTTP incoming data.'
        content = self.__content.read(num_bytes)
        self.__len -= num_bytes
        return content


class NetworkAPITestClient(Client):

    def putXML(self, url, data=None, **extra):
        """ Converte o dicionario data para XML e faz um requisição PUT """
        if type(data) == dict:
            data = dict2xml(data)

        return self.put(url, data=data, content_type=CONTENT_APPLICATION_XML)

    def postXML(self, url, data=None, **extra):
        """ Converte o dicionario data para XML e faz um requisição POST """
        if type(data) == dict:
            data = dict2xml(data)

        return self.post(url, data=data, content_type=CONTENT_APPLICATION_XML)

    def deleteXML(self, url, data=None, **extra):
        """ Converte o dicionario data para XML e faz um requisição PUT """
        if type(data) == dict:
            data = dict2xml(data)

        return self.delete_client(url, data=data, content_type=CONTENT_APPLICATION_XML)

    def delete_client(self, path, data={}, content_type=MULTIPART_CONTENT,
                      follow=False, **extra):
        """
        Requests a response from the server using POST.
        """
        response = self.delete_request(
            path, data=data, content_type=content_type, **extra)
        if follow:
            response = self._handle_redirects(response, **extra)
        return response

    def delete_request(self, path, data={}, content_type=MULTIPART_CONTENT,
                       **extra):
        'Construct a POST request.'

        post_data = self._encode_data(data, content_type)

        parsed = urlparse(path)
        r = {
            'CONTENT_LENGTH': len(post_data),
            'CONTENT_TYPE': content_type,
            'PATH_INFO': self._get_path(parsed),
            'QUERY_STRING': parsed[4],
            'REQUEST_METHOD': 'DELETE',
            'wsgi.input': FakePayload(post_data),
        }
        r.update(extra)
        return self.request(**r)


class CodeError(CodeError):

    XML_ERROR = 3

    PERMISSION_ADMINISTRATIVE_NOT_FOUND = 189
    PERMISSION_ADMINISTRATIVE_DUPLICATE = 351
    PERMISSION_NOT_FOUND = 350
    UGROUP_NOT_FOUND = 180
    USER_NOT_FOUND = 177
    USER_DUPLICATE = 179
    USER_GROUP_RELATED = 224
    FILTER_NOT_FOUND = 339
    FILTER_DUPLICATE = 344
    EQUIPMENT_TYPE_NOT_FOUND = 100
    EQUIPMENT_NOT_FOUND = 117
    FILTER_EQUIPTYPE_CANT_DISSOCIATE = 348
    OPTION_VIP_NOT_FOUND = 289
    ENV_VIP_NOT_FOUND = 283
    USER_GROUP_NOT_FOUND = 180

    GROUP_L3_NOT_FOUND = 160
    GROUP_L3_DUPLICATE = 169

    DIVISION_DC_NOT_FOUND = 164
    DIVISION_DC_DUPLICATE = 175

    LOGICAL_ENVIRONMENT_NOT_FOUND = 162
    LOGICAL_ENVIRONMENT_DUPLICATE = 173
    ENVIRONMENT_NOT_FOUND = 112

    USER_GROUP_ALREADY_NAME = 182
    USER_GROUP_DUPLICATE = 183
    USER_GROUP_NO_ASSOCIATE = 184

    SCRIPT_TYPE_NOT_FOUND = 158
    SCRIPT_TYPE_DUPLICATE = 193
    SCRIPT_TYPE_RELATED = 196

    SCRIPT_NOT_FOUND = 165
    SCRIPT_DUPLICATE = 250
    SCRIPT_RELATED = 197

    BRAND_NOT_FOUND = 167
    BRAND_DUPLICATE = 251
    BRAND_RELATED = 199

    MODEL_NOT_FOUND = 101
    MODEL_DUPLICATE = 252
    MODEL_EQUIPMENT_RELATED = 202

    ACCESS_TYPE_NOT_FOUND = 171
    ACCESS_TYPE_DUPLICATE = 203

    INTERFACE_NOT_FOUND = 141
    INTERFACE_RELATED = 214
    INTERFACE_FRONT_NOT_FOUND = 212
    INTERFACE_BACK_NOT_FOUND = 213
    INTERFACE_NOT_CONNECTED = 307

    EQUIPMENT_ACCESS_NOT_FOUND = 303

    VLAN_NOT_FOUND = 116
    VLAN_DUPLICATE = 108
    VLAN_NUMBER_DUPLICATE = 315
    VLAN_ACL_DUPLICATE = 311
    VLAN_HAS_NO_NETWORKS = 281
    VLAN_INACTIVE = 368

    HEALTHCHECKEXPECT_NOT_FOUND = 124

    IP_CONFIG_NOT_FOUND = 301

    NETWORK_IPV4_NOT_FOUND = 281
    NETWORK_IPV6_NOT_FOUND = 286

    NETWORK_TYPE_NOT_FOUND = 111
    NETWORK_TYPE_NAME_DUPLICATED = 253

    IP_NOT_FOUND = 119

    EQUIPMENT_GROUP_NOT_FOUND = 102

    EQUIPMENT_GROUP_RIGHTS_NOT_FOUND = 258

    VIP_REQUEST_NOT_FOUND = 152
    VIP_REQUEST_NOT_YET_VALIDATED = 191
    VIP_REQUEST_ALREADY_CREATED = 192
    VIP_REQUEST_NOT_CREATED = 322

    HEALTHCHECK_EXPECT_HTTP_NOT_NONE = 277
    VIP_ENVIRONMENT_NOT_FOUND_IN_VIP_ADD = 316
    VIP_ENVIRONMENT_NOT_FOUND_IN_VIP_EDIT = 316
    VIP_INVALID_CACHE_VALUE = 128
    VIP_INVALID_BAL_METHOD_VALUE = 131
    VIP_INVALID_PERSISTENCE_VALUE = 132
    VIP_INVALID_HEALTHCHECK_TYPE_VALUE = 275
    HEALTHCHECK_EXPECT_NOT_HTTP_NOT_NONE = 276
    VIP_INVALID_TIMEOUT_VALUE = 135
    VIP_INVALID_SERVICE_PORTS_VALUE = 138
    VIP_REALS_PRIORITY_WRONG_NUMBER_LIST = 272
    VIP_REALS_WEIGHT_WRONG_NUMBER_LIST = 274

    VIP_EDIT_REALS_PRIORITY_INCONSISTENCY = 329
    VIP_EDIT_REALS_WEIGHT_INCONSISTENCY = 330
    VIP_OLD_INVALID_REALS = 151

    IP_NOT_REGISTERED_FOR_EQUIP = 118

    IP_NOT_RELATED_ENVIRONMENT_VIP = 334

    VIP_INVALID_PARAMETER = 332

    VIRTUAL_GROUP_EQUIP_NAME_REQUIRED = 105

    RULE_NOT_FIND = 358
    BLOCK_NOT_FOUND = 359

    VLANNUMBERNOTAVAILABLEERROR = 109
    VIPREQUESTBLOCKALREADYINRULE = 361
    VIPREQUESTNOBLOCKINRULE = 362
    NETWORK_REMOVE_INACTIVE = 363

    CONFIG_ENVIRONMENT_ALREADY_EXISTS = 302


class BasicTest():

    KEY_ATTR = ''
    CODE_ERROR_NOT_FOUND = 0

    NEGATIVE_ATTR = '-1'
    LETTER_ATTR = 'anb'
    ZERO_ATTR = 0
    EMPTY_ATTR = '  '
    NONE_ATTR = None

    def _not_found(self, response, code_error=None):
        if code_error is None:
            code_error = self.CODE_ERROR_NOT_FOUND
        valid_response(response, status_code=httplib.INTERNAL_SERVER_ERROR)
        assert_response_error(response, codigo=code_error)

    def _attr_invalid(self, response, code_error=None):
        if code_error is None:
            code_error = CodeError.INVALID_VALUE_ERROR

        valid_response(response, status_code=httplib.INTERNAL_SERVER_ERROR)
        assert_response_error(response, codigo=code_error)

    def _attr_nonexistent(self):
        with pytest.raises(self.OBJ.DoesNotExist):
            self.OBJ.objects.get(pk=self.ID_NONEXISTENT)

        mock = self.mock_valid()
        mock[self.KEY_ATTR] = self.ID_NONEXISTENT
        return mock

    def _attr_negative(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = self.NEGATIVE_ATTR
        return mock

    def _attr_letter(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = self.LETTER_ATTR
        return mock

    def _attr_zero(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = self.ZERO_ATTR
        return mock

    def _attr_empty(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = self.EMPTY_ATTR
        return mock

    def _attr_none(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = None
        return mock

    def mock_valid(self):
        mock = {}
        return mock

    def process_save_not_found(self, mock):
        response = self.save({self.XML_KEY: mock})
        self._not_found(response)

    def process_save_attr_invalid(self, mock, code_error=None):
        response = self.save({self.XML_KEY: mock})

        if code_error is not None:
            self._attr_invalid(response, code_error)

        else:
            self._attr_invalid(response)

    def process_alter_not_found(self, idt, mock):
        response = self.alter(idt, {self.XML_KEY: mock})
        self._not_found(response)

    def process_alter_attr_invalid(self, idt, mock, code_error=None):
        response = self.alter(idt, {self.XML_KEY: mock})

        if code_error is not None:
            self._attr_invalid(response, code_error)

        else:
            self._attr_invalid(response)


class AttrTest(BasicTest):

    # --------- SAVE ---------

    def save_attr_nonexistent(self):
        mock = self._attr_nonexistent()
        self.process_save_not_found(mock)

    def save_attr_negative(self):
        mock = self._attr_negative()
        self.process_save_attr_invalid(mock)

    def save_attr_letter(self):
        mock = self._attr_letter()
        self.process_save_attr_invalid(mock)

    def save_attr_zero(self):
        mock = self._attr_zero()
        self.process_save_attr_invalid(mock)

    def save_attr_empty(self):
        mock = self._attr_empty()
        self.process_save_attr_invalid(mock)

    def save_attr_none(self):
        mock = self._attr_none()
        self.process_save_attr_invalid(mock)

    # --------- ALTER ---------

    def alter_attr_nonexistent(self, idt):
        mock = self._attr_nonexistent()
        self.process_alter_not_found(idt, mock)

    def alter_attr_negative(self, idt):
        mock = self._attr_negative()
        self.process_alter_attr_invalid(idt, mock)

    def alter_attr_letter(self, idt):
        mock = self._attr_letter()
        self.process_alter_attr_invalid(idt, mock)

    def alter_attr_zero(self, idt):
        mock = self._attr_zero()
        self.process_alter_attr_invalid(idt, mock)

    def alter_attr_empty(self, idt):
        mock = self._attr_empty()
        self.process_alter_attr_invalid(idt, mock)

    def alter_attr_none(self, idt):
        mock = self._attr_none()
        self.process_alter_attr_invalid(idt, mock)


class ConsultationTest(BasicTestCase, BasicTest):

    def get_by_id_nonexistent(self):
        response = self.get_by_id(self.ID_NONEXISTENT)
        self._not_found(response)

    def get_by_id_negative(self):
        response = self.get_by_id(self.NEGATIVE_ATTR)
        self._attr_invalid(response)

    def get_by_id_letter(self):
        response = self.get_by_id(self.LETTER_ATTR)
        self._attr_invalid(response)

    def get_by_id_zero(self):
        response = self.get_by_id(self.ZERO_ATTR)
        self._attr_invalid(response)

    def get_by_id_empty(self):
        response = self.get_by_id(self.EMPTY_ATTR)
        self._attr_invalid(response)


class RemoveTest(BasicTestCase, BasicTest):

    def remove_nonexistent(self):
        response = self.remove(self.ID_NONEXISTENT)
        self._not_found(response)

    def remove_negative(self):
        response = self.remove(self.NEGATIVE_ATTR)
        self._attr_invalid(response)

    def remove_letter(self):
        response = self.remove(self.LETTER_ATTR)
        self._attr_invalid(response)

    def remove_zero(self):
        response = self.remove(self.ZERO_ATTR)
        self._attr_invalid(response)

    def remove_empty(self):
        response = self.remove(self.EMPTY_ATTR)
        self._attr_invalid(response)
