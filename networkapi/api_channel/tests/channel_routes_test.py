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

from json import dumps
from json import loads

from django.test.client import Client

from rest_framework.exceptions import AuthenticationFailed

from networkapi.test.test_case import NetworkApiTestCase
from networkapi.api_channel.views import DeployChannelConfV3View


class TestChannelRoutes(NetworkApiTestCase):
    """ Class to test Channels http routes """

    fixtures = [
        'networkapi/system/fixtures/initial_variables.json',
        'networkapi/usuario/fixtures/initial_usuario.json',
        'networkapi/grupo/fixtures/initial_ugrupo.json',
        'networkapi/usuario/fixtures/initial_usuariogrupo.json',
        'networkapi/grupo/fixtures/initial_permissions.json',
        'networkapi/grupo/fixtures/initial_permissoes_administrativas.json',

        "networkapi/api_channel/fixtures/initial_channel.json"
    ]

    def setUp(self):
        self.client = Client()
        self.auth = self.get_http_authorization('test')

    def test_should_receive_method_not_allowed(self):
        """ Should receive method not allowed """

        response = self.client.get(
            '/api/v3/interface/channel/1/deploy/',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.auth)

        self.assertEqual(405, response.status_code)

    def test_should_not_allow_unauthenticated_user(self):
        """ Should not allow requests from an unauthenticated user """

        with self.assertRaises(AuthenticationFailed):

            response = self.client.put(
                '/api/v3/interface/channel/1/deploy/',
                data=dumps({}),
                content_type='application/json',
                HTTP_AUTHORIZATION=self.get_http_authorization('fake'))

    def test_should_get_a_channel_by_id(self):
        """ Should get a Channel by id """

        response = self.client.get(
            '/api/v3/interface/channel/1/',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.auth)

        self.assertEqual(200, response.status_code)

    def test_should_not_get_a_channel_by_id(self):
        """ Should not get a Channel with an unexisting id """

        response = self.client.get(
            '/api/v3/interface/channel/0/',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.auth)

        self.assertEqual(404, response.status_code)

    def test_should_get_a_channel_by_name(self):
        """ Should get a channel by Name """
        response = self.client.get(
            '/api/v3/interface/channel/tor42/',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.auth)

        self.assertEqual(200, response.status_code)
        content = loads(response.content)
        self.assertEqual(content["channel"]["id"], 1)

    def test_should_not_get_a_channel_by_name(self):
        """ Should not get a channel with an unexisting Name """
        response = self.client.get(
            '/api/v3/interface/channel/fakechannel/',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.auth)

        self.assertEqual(404, response.status_code)
        channel = loads(response.content)
        self.assertIn("error", channel)

    def test_should_post_a_channel(self):
        """ Should post a Channel """

        response = self.client.post(
            '/api/v3/interface/channel/1/',
            content_type='application/json',
            data=dumps({}),
            HTTP_AUTHORIZATION=self.auth)

        self.assertEqual(201, response.status_code)

    def test_should_update_a_channel(self):
        """ Should update a Channel """

        response = self.client.put(
            '/api/v3/interface/channel/1/',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.auth)

        self.assertEqual(200, response.status_code)

    def test_should_delete_a_channel(self):
        """ Should delete a Channel """

        response = self.client.delete(
            '/api/v3/interface/channel/1/',
            HTTP_AUTHORIZATION=self.auth)

        self.assertEqual(404, response.status_code)
