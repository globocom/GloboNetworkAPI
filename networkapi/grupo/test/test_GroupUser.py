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


from networkapi.grupo.models import UGrupo
from networkapi.test import BasicTestCase, RemoveTest, AttrTest, CodeError, ConsultationTest, CLIENT_TYPES, me
from networkapi.test.functions import valid_content, valid_response, valid_get_all, string_generator
import httplib


class GroupUserConfigTest(BasicTestCase):

    # Constants
    fixtures = ['networkapi/grupo/fixtures/initial_data.yaml']
    XML_KEY = "user_group"

    ID_VALID = 1
    ID_ALTER_VALID = 5
    ID_REMOVE_VALID = 8

    OBJ = UGrupo

    # Urls
    URL_SAVE = "/ugroup/"
    URL_ALTER = "/ugroup/%s/"
    URL_REMOVE = "/ugroup/%s/"
    URL_GET_BY_ID = "/ugroup/get/%s/"
    URL_GET_ALL = "/ugroup/all/"

    def mock_valid(self):
        mock = {}
        mock['nome'] = "mock"
        mock['leitura'] = "S"
        mock['escrita'] = "S"
        mock['edicao'] = "S"
        mock['exclusao'] = "S"
        return mock

    def valid_attr(self, mock, obj):
        assert mock["nome"] == obj["nome"]
        assert mock["leitura"] == obj["leitura"]
        assert mock["escrita"] == obj["escrita"]
        assert mock["edicao"] == obj["edicao"]
        assert mock["exclusao"] == obj["exclusao"]


class GroupUserConsultationTest(GroupUserConfigTest, ConsultationTest):

    CODE_ERROR_NOT_FOUND = CodeError.USER_GROUP_NOT_FOUND

    def test_get_all(self):
        response = self.get_all()
        valid_response(response)
        content = valid_content(response, self.XML_KEY)
        valid_get_all(content, self.OBJ)

    def test_get_all_no_permission(self):
        response = self.get_all(CLIENT_TYPES.NO_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_get_all_no_read_permission(self):
        response = self.get_all(CLIENT_TYPES.NO_READ_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_get_by_id_valid(self):
        response = self.get_by_id(self.ID_VALID)
        valid_response(response)
        valid_content(response, self.XML_KEY)

    def test_get_by_id_no_permission(self):
        response = self.get_by_id(self.ID_VALID, CLIENT_TYPES.NO_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_get_by_id_no_read_permission(self):
        response = self.get_by_id(
            self.ID_VALID, CLIENT_TYPES.NO_READ_PERMISSION)
        valid_response(response, httplib.PAYMENT_REQUIRED)

    def test_get_by_id_nonexistent(self):
        self.get_by_id_nonexistent()

    def test_get_by_id_negative(self):
        self.get_by_id_negative()

    def test_get_by_id_letter(self):
        self.get_by_id_letter()

    def test_get_by_id_zero(self):
        self.get_by_id_zero()

    def test_get_by_id_empty(self):
        self.get_by_id_empty()


class GroupUserTest(GroupUserConfigTest):

    CODE_ERROR_ALREADY_NAME = CodeError.USER_GROUP_ALREADY_NAME

    def test_save_valid(self):
        mock = self.mock_valid()
        response = self.save({self.XML_KEY: mock})
        valid_response(response)
        group_user = valid_content(response, self.XML_KEY)

        response = self.get_by_id(group_user['id'])
        valid_response(response)
        content = valid_content(response, self.XML_KEY)
        self.valid_attr(mock, content)

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
        mock["nome"] = "GroupUserAlter"
        response = self.alter(self.ID_ALTER_VALID, {self.XML_KEY: mock})
        valid_response(response)

        response = self.get_by_id(self.ID_ALTER_VALID)
        valid_response(response)
        ugrp = valid_content(response, "user_group")

        self.valid_attr(mock, ugrp)

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


class GroupUserRemoveTest(GroupUserConfigTest, RemoveTest):

    CODE_ERROR_NOT_FOUND = CodeError.USER_GROUP_NOT_FOUND

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


class GroupUserAttrNomeTest(GroupUserConfigTest, AttrTest):

    KEY_ATTR = "nome"

    def test_save_maxsize(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = string_generator(101)
        self.process_save_attr_invalid(mock)

    def test_save_minsize(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = string_generator(2)
        self.process_save_attr_invalid(mock)

    def test_save_unique(self):
        response = self.get_by_id(self.ID_VALID)
        valid_response(response)
        ugrp = valid_content(response, self.XML_KEY)

        mock = self.mock_valid()
        mock["nome"] = ugrp["nome"]
        self.process_save_attr_invalid(mock, CodeError.USER_GROUP_ALREADY_NAME)

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

    def test_alter_unique(self):
        response = self.get_by_id(self.ID_VALID)
        valid_response(response)
        ugrp = valid_content(response, self.XML_KEY)

        mock = self.mock_valid()
        mock["nome"] = ugrp["nome"]
        self.process_alter_attr_invalid(
            mock, CodeError.USER_GROUP_ALREADY_NAME)

    def test_alter_empty(self):
        self.alter_attr_empty(self.ID_ALTER_VALID)

    def test_alter_none(self):
        self.alter_attr_none(self.ID_ALTER_VALID)


@me
class GroupUserAttrLeituraTest(GroupUserConfigTest, AttrTest):

    KEY_ATTR = "leitura"

    def test_save_invalid_string(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = string_generator(5)
        self.process_save_attr_invalid(mock)

    def test_save_invalid_bool_0(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = '0'
        self.process_save_attr_invalid(mock)

    def test_save_invalid_bool_1(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = '1'
        self.process_save_attr_invalid(mock)

    def test_save_invalid_bool_false(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = 'False'
        self.process_save_attr_invalid(mock)

    def test_save_invalid_bool_true(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = 'True'
        self.process_save_attr_invalid(mock)

    def test_save_empty(self):
        self.save_attr_empty()

    def test_save_none(self):
        self.save_attr_none()

    def test_alter_invalid_string(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = string_generator(5)
        self.process_alter_attr_invalid(self.ID_ALTER_VALID, mock)

    def test_alter_invalid_bool_0(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = '0'
        self.process_alter_attr_invalid(self.ID_ALTER_VALID, mock)

    def test_alter_invalid_bool_1(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = '1'
        self.process_alter_attr_invalid(self.ID_ALTER_VALID, mock)

    def test_alter_invalid_bool_false(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = 'False'
        self.process_alter_attr_invalid(self.ID_ALTER_VALID, mock)

    def test_alter_invalid_bool_true(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = 'True'
        self.process_alter_attr_invalid(self.ID_ALTER_VALID, mock)

    def test_alter_empty(self):
        self.alter_attr_empty(self.ID_ALTER_VALID)

    def test_alter_none(self):
        self.alter_attr_none(self.ID_ALTER_VALID)


@me
class GroupUserAttrEscritaTest(GroupUserConfigTest, AttrTest):

    KEY_ATTR = "escrita"

    def test_save_invalid_string(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = string_generator(5)
        self.process_save_attr_invalid(mock)

    def test_save_invalid_bool_0(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = '0'
        self.process_save_attr_invalid(mock)

    def test_save_invalid_bool_1(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = '1'
        self.process_save_attr_invalid(mock)

    def test_save_invalid_bool_false(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = 'False'
        self.process_save_attr_invalid(mock)

    def test_save_invalid_bool_true(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = 'True'
        self.process_save_attr_invalid(mock)

    def test_save_empty(self):
        self.save_attr_empty()

    def test_save_none(self):
        self.save_attr_none()

    def test_alter_invalid_string(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = string_generator(5)
        self.process_alter_attr_invalid(self.ID_ALTER_VALID, mock)

    def test_alter_invalid_bool_0(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = '0'
        self.process_alter_attr_invalid(self.ID_ALTER_VALID, mock)

    def test_alter_invalid_bool_1(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = '1'
        self.process_alter_attr_invalid(self.ID_ALTER_VALID, mock)

    def test_alter_invalid_bool_false(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = 'False'
        self.process_alter_attr_invalid(self.ID_ALTER_VALID, mock)

    def test_alter_invalid_bool_true(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = 'True'
        self.process_alter_attr_invalid(self.ID_ALTER_VALID, mock)

    def test_alter_empty(self):
        self.alter_attr_empty(self.ID_ALTER_VALID)

    def test_alter_none(self):
        self.alter_attr_none(self.ID_ALTER_VALID)


@me
class GroupUserAttrEdicaoTest(GroupUserConfigTest, AttrTest):

    KEY_ATTR = "edicao"

    def test_save_invalid_string(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = string_generator(5)
        self.process_save_attr_invalid(mock)

    def test_save_invalid_bool_0(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = '0'
        self.process_save_attr_invalid(mock)

    def test_save_invalid_bool_1(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = '1'
        self.process_save_attr_invalid(mock)

    def test_save_invalid_bool_false(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = 'False'
        self.process_save_attr_invalid(mock)

    def test_save_invalid_bool_true(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = 'True'
        self.process_save_attr_invalid(mock)

    def test_save_empty(self):
        self.save_attr_empty()

    def test_save_none(self):
        self.save_attr_none()

    def test_alter_invalid_string(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = string_generator(5)
        self.process_alter_attr_invalid(self.ID_ALTER_VALID, mock)

    def test_alter_invalid_bool_0(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = '0'
        self.process_alter_attr_invalid(self.ID_ALTER_VALID, mock)

    def test_alter_invalid_bool_1(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = '1'
        self.process_alter_attr_invalid(self.ID_ALTER_VALID, mock)

    def test_alter_invalid_bool_false(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = 'False'
        self.process_alter_attr_invalid(self.ID_ALTER_VALID, mock)

    def test_alter_invalid_bool_true(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = 'True'
        self.process_alter_attr_invalid(self.ID_ALTER_VALID, mock)

    def test_alter_empty(self):
        self.alter_attr_empty(self.ID_ALTER_VALID)

    def test_alter_none(self):
        self.alter_attr_none(self.ID_ALTER_VALID)


@me
class GroupUserAttrExclusaoTest(GroupUserConfigTest, AttrTest):

    KEY_ATTR = "exclusao"

    def test_save_invalid_string(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = string_generator(5)
        self.process_save_attr_invalid(mock)

    def test_save_invalid_bool_0(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = '0'
        self.process_save_attr_invalid(mock)

    def test_save_invalid_bool_1(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = '1'
        self.process_save_attr_invalid(mock)

    def test_save_invalid_bool_false(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = 'False'
        self.process_save_attr_invalid(mock)

    def test_save_invalid_bool_true(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = 'True'
        self.process_save_attr_invalid(mock)

    def test_save_empty(self):
        self.save_attr_empty()

    def test_save_none(self):
        self.save_attr_none()

    def test_alter_invalid_string(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = string_generator(5)
        self.process_alter_attr_invalid(self.ID_ALTER_VALID, mock)

    def test_alter_invalid_bool_0(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = '0'
        self.process_alter_attr_invalid(self.ID_ALTER_VALID, mock)

    def test_alter_invalid_bool_1(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = '1'
        self.process_alter_attr_invalid(self.ID_ALTER_VALID, mock)

    def test_alter_invalid_bool_false(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = 'False'
        self.process_alter_attr_invalid(self.ID_ALTER_VALID, mock)

    def test_alter_invalid_bool_true(self):
        mock = self.mock_valid()
        mock[self.KEY_ATTR] = 'True'
        self.process_alter_attr_invalid(self.ID_ALTER_VALID, mock)

    def test_alter_empty(self):
        self.alter_attr_empty(self.ID_ALTER_VALID)

    def test_alter_none(self):
        self.alter_attr_none(self.ID_ALTER_VALID)
