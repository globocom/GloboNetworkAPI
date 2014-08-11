# -*- coding:utf-8 -*-

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


from networkapi.grupo.models import Permission
from networkapi.test import BasicTestCase, CodeError, ConsultationTest, CLIENT_TYPES, me
from networkapi.test.functions import valid_content, valid_response, valid_get_all
import httplib


class PermissionConfigTest(BasicTestCase):

    # Constants
    fixtures = ['networkapi/grupo/fixtures/initial_data.yaml']
    XML_KEY = ""
    ID_VALID = 1
    OBJ = Permission

    # Urls
    URL_SAVE = ""
    URL_ALTER = ""
    URL_REMOVE = ""
    URL_GET_BY_ID = ""
    URL_GET_ALL = "/perms/all/"

    def mock_valid(self):
        mock = {}
        mock['id'] = 1
        mock['function'] = "mock"
        return mock


class PermissionConsultationTest(PermissionConfigTest, ConsultationTest):

    CODE_ERROR_NOT_FOUND = CodeError.PERMISSION_NOT_FOUND

    def test_get_all(self):
        response = self.get_all()
        valid_response(response)
        content = valid_content(response, "perms")
        valid_get_all(content, self.OBJ)

    def test_get_all_no_permission(self):
        response = self.get_all(CLIENT_TYPES.NO_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_get_all_no_read_permission(self):
        response = self.get_all(CLIENT_TYPES.NO_READ_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_get_all_no_active(self):
        response = self.get_all(CLIENT_TYPES.NO_ACTIVE)
        valid_response(response, httplib.UNAUTHORIZED)
