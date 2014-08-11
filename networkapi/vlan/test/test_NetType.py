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


from django.forms.models import model_to_dict
from networkapi.vlan.models import TipoRede
from networkapi.test import BasicTestCase, me, CodeError, me, AttrTest, RemoveTest, CLIENT_TYPES
from networkapi.test.functions import valid_content, valid_response, valid_get_all, string_generator
import httplib


class NetTypeConfigTest(BasicTestCase):

    # Constants
    fixtures = ['networkapi/vlan/fixtures/initial_data.yaml']
    XML_KEY = "net_type"
    ID_VALID = 1
    ID_ALTER_VALID = 3
    ID_REMOVE_VALID = 4
    OBJ = TipoRede

    # Urls
    URL_GET_ALL = "/net_type/"
    URL_SAVE = "/net_type/"
    URL_ALTER = "/net_type/%s/"
    URL_REMOVE = "/net_type/%s/"

    def mock_valid(self):
        mock = {}
        mock["name"] = u"mock"
        return mock

    def mock_valid_alter(self):
        mock = {}
        mock["name"] = u"mockAlter"
        return mock

    def valid_attr(self, mock, obj):
        assert mock["name"] == obj["tipo_rede"]


class NetTypeConsultationTest(NetTypeConfigTest):

    def test_get_all(self):
        response = self.get_all()
        valid_response(response)
        content = valid_content(response, self.XML_KEY)
        valid_get_all(content, self.OBJ)

    def test_get_all_inactive(self):
        response = self.get_all(CLIENT_TYPES.NO_ACTIVE)
        valid_response(response, httplib.UNAUTHORIZED)

    def test_get_all_no_permission(self):
        response = self.get_all(CLIENT_TYPES.NO_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_get_all_no_read_permission(self):
        response = self.get_all(CLIENT_TYPES.NO_READ_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)


class NetTypeTest(NetTypeConfigTest):

    def test_save_valid(self):
        mock = self.mock_valid()
        response = self.save({self.XML_KEY: mock})
        valid_response(response)
        content = valid_content(response, self.XML_KEY)

        nt = TipoRede.get_by_pk(content["id"])
        self.valid_attr(mock, model_to_dict(nt))

    def test_save_no_permission(self):
        mock = self.mock_valid()
        response = self.save({self.XML_KEY: mock}, CLIENT_TYPES.NO_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_save_no_write_permission(self):
        mock = self.mock_valid()
        response = self.save(
            {self.XML_KEY: mock}, CLIENT_TYPES.NO_WRITE_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_alter_valid(self):
        mock = self.mock_valid_alter()
        response = self.alter(self.ID_ALTER_VALID, {self.XML_KEY: mock})
        valid_response(response)

        nt = TipoRede.get_by_pk(self.ID_ALTER_VALID)
        self.valid_attr(mock, model_to_dict(nt))

    def test_alter_no_permission(self):
        mock = self.mock_valid_alter()
        response = self.alter(
            self.ID_ALTER_VALID, {self.XML_KEY: mock}, CLIENT_TYPES.NO_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_alter_no_write_permission(self):
        mock = self.mock_valid_alter()
        response = self.alter(
            self.ID_ALTER_VALID, {self.XML_KEY: mock}, CLIENT_TYPES.NO_WRITE_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)


class NetTypeRemoveTest(NetTypeConfigTest, RemoveTest):

    CODE_ERROR_NOT_FOUND = CodeError.NETWORK_TYPE_NOT_FOUND

    def test_remove_valid(self):
        response = self.remove(self.ID_REMOVE_VALID)
        valid_response(response)

    def test_remove_no_permission(self):
        response = self.remove(
            self.ID_REMOVE_VALID, CLIENT_TYPES.NO_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_remove_no__write_permission(self):
        response = self.remove(
            self.ID_REMOVE_VALID, CLIENT_TYPES.NO_WRITE_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_remove_nonexistent(self):
        self.remove_nonexistent()

    def test_remove_negative(self):
        self.remove_negative()

    def test_remove_letter(self):
        self.remove_letter()

    def test_remove_zero(self):
        self.remove_zero()

    def test_remove_empty(self):
        self.remove_empty()


class NetTypeAttrTipoRedeTest(NetTypeConfigTest, AttrTest):

    KEY_ATTR = "name"

    def test_save_maxsize(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = string_generator(101)
        self.process_save_attr_invalid(mock)

    def test_save_minsize(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = string_generator(2)
        self.process_save_attr_invalid(mock)

    def test_save_name_duplicated(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = 'Barramento'
        self.process_save_attr_invalid(
            mock, CodeError.NETWORK_TYPE_NAME_DUPLICATED)

    def test_save_empty(self):
        self.save_attr_empty()

    def test_save_none(self):
        self.save_attr_none()

    def test_alter_maxsize(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = string_generator(101)
        self.process_alter_attr_invalid(self.ID_ALTER_VALID, mock)

    def test_alter_minsize(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = string_generator(2)
        self.process_alter_attr_invalid(self.ID_ALTER_VALID, mock)

    def test_alter_name_duplicated(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = 'Barramento'
        self.process_alter_attr_invalid(
            self.ID_ALTER_VALID, mock, CodeError.NETWORK_TYPE_NAME_DUPLICATED)

    def test_alter_empty(self):
        self.alter_attr_empty(self.ID_ALTER_VALID)

    def test_alter_none(self):
        self.alter_attr_none(self.ID_ALTER_VALID)
