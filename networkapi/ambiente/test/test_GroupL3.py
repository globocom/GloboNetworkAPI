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


from networkapi.ambiente.models import GrupoL3
from networkapi.test import BasicTestCase, AttrTest, CodeError, ConsultationTest, RemoveTest, CLIENT_TYPES, me, bug
from networkapi.test.functions import valid_content, valid_response, valid_get_all, string_generator
import httplib


class GroupL3ConfigTest(BasicTestCase):

    # Constants
    fixtures = ['networkapi/ambiente/fixtures/initial_data.yaml']
    XML_KEY = "group_l3"
    ID_VALID = 1
    ID_REMOVE_VALID = 3
    ID_ALTER_VALID = 2
    OBJ = GrupoL3

    # Urls
    URL_SAVE = "/groupl3/"
    URL_ALTER = "/groupl3/%s/"
    URL_REMOVE = "/groupl3/%s/"
    URL_GET_BY_ID = ""
    URL_GET_ALL = "/groupl3/all/"

    def mock_valid(self):
        mock = {}
        mock['name'] = "mock"
        return mock

    def valid_attr(self, mock, obj):
        assert mock["name"] == obj["nome"]


class GroupL3ConsultationTest(GroupL3ConfigTest, ConsultationTest):

    CODE_ERROR_NOT_FOUND = CodeError.GROUP_L3_NOT_FOUND

    def test_get_all(self):
        response = self.get_all()
        valid_response(response)
        content = valid_content(response, "group_l3")
        valid_get_all(content, self.OBJ)

    def test_get_all_no_permission(self):
        response = self.get_all(CLIENT_TYPES.NO_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_get_all_no_read_permission(self):
        response = self.get_all(CLIENT_TYPES.NO_READ_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)


class GroupL3Test(GroupL3ConfigTest):

    def test_save_valid(self):
        mock = self.mock_valid()
        response = self.save({self.XML_KEY: mock})
        valid_response(response)
        groupl3 = valid_content(response, "group_l3")

        response = self.get_all()
        valid_response(response)
        content = valid_content(response, "group_l3")

        for grp in content:
            if grp["id"] == groupl3["id"]:
                self.valid_attr(mock, grp)
                break

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
        mock = self.mock_valid()
        mock["name"] = "GroupAlter"
        response = self.alter(self.ID_ALTER_VALID, {self.XML_KEY: mock})
        valid_response(response)

        response = self.get_all()
        valid_response(response)
        content = valid_content(response, "group_l3")

        for grp in content:
            if grp["id"] == self.ID_ALTER_VALID:
                self.valid_attr(mock, grp)
                break

    def test_alter_no_permission(self):
        mock = self.mock_valid()
        response = self.alter(
            self.ID_ALTER_VALID, {self.XML_KEY: mock}, CLIENT_TYPES.NO_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_alter_no_write_permission(self):
        mock = self.mock_valid()
        response = self.alter(
            self.ID_ALTER_VALID, {self.XML_KEY: mock}, CLIENT_TYPES.NO_WRITE_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)


class GroupL3RemoveTest(GroupL3ConfigTest, RemoveTest):

    CODE_ERROR_NOT_FOUND = CodeError.GROUP_L3_NOT_FOUND

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


class GroupL3AttrNameTest(GroupL3ConfigTest, AttrTest):

    KEY_ATTR = "name"

    def test_save_maxsize(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = string_generator(81)
        self.process_save_attr_invalid(mock)

    def test_save_minsize(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = string_generator(1)
        self.process_save_attr_invalid(mock)

    def test_save_unique(self):
        response = self.get_all()
        valid_response(response)
        content = valid_content(response, "group_l3")

        grp = content[0]

        mock = self.mock_valid()
        mock["name"] = grp["nome"]

        self.process_save_attr_invalid(mock, CodeError.GROUP_L3_DUPLICATE)

    def test_save_empty(self):
        self.save_attr_empty()

    def test_save_none(self):
        self.save_attr_none()

    def test_alter_maxsize(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = string_generator(81)
        self.process_alter_attr_invalid(self.ID_ALTER_VALID, mock)

    def test_alter_minsize(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = string_generator(1)
        self.process_alter_attr_invalid(self.ID_ALTER_VALID, mock)

    def test_alter_unique(self):
        response = self.get_all()
        valid_response(response)
        content = valid_content(response, "group_l3")

        grp = content[0]

        mock = self.mock_valid()
        mock["name"] = grp["nome"]
        self.process_alter_attr_invalid(
            self.ID_ALTER_VALID, mock, CodeError.GROUP_L3_DUPLICATE)

    def test_alter_empty(self):
        self.alter_attr_empty(self.ID_ALTER_VALID)

    def test_alter_none(self):
        self.alter_attr_none(self.ID_ALTER_VALID)
